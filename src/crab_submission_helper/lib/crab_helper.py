#!/usr/bin/env python3
import subprocess
import glob
import datetime
import logging
from typing import Optional, Union, Callable, Any, Dict
from pathlib import Path

from . import parse_helper as parser
from . import generators as gen
from . import config as conf

logger = logging.getLogger(__name__)

def batch_submit_jobs(
    batch_file: str,
    template_files: Dict[str, str],
    generating_functions: Union[Callable, list[Callable], None] = [gen.add_dataset, gen.add_request_name, gen.add_lumi_mask],
    test: bool = False,
    run_directory=None
):
    """
    Submit a number of crab jobs all at once. A copy of your generated template files
    will be placed inside of data/generated/<timestamp> for debugging or recovery.

    batch_file: yaml file that contains the values to replace
    template_files: dict mapping template file paths to output paths
    generating_functions: optional callable or list of callables to generate dynamic values
    """

    # Parse the YAML — returns a list of job dictionaries directly
    job_replacements = parser.parse_yaml(batch_file)

    # Normalize generating_functions to a list
    if generating_functions is not None and not isinstance(generating_functions, list):
        generating_functions = [generating_functions]

    # Apply generators in order
    if generating_functions:
        for func in generating_functions:
            job_replacements = [
                gen.generate_template_values(job_dict, func) for job_dict in job_replacements
            ]
    print(job_replacements)
    logging.info(f"Processed {len(job_replacements)} job replacements.")

    # Save templates for each job
    timestamp_dir = conf.PROJECT_ROOT / "src" / "crab_submission_helper" / "data" / "generated" / datetime.datetime.now().strftime('%Y%m%d_%H%M')
    timestamp_dir.mkdir(parents=True, exist_ok=True)
    for job_dict in job_replacements:
        for template_path, output_path in template_files.items():
            # Save one copy for use in job
            parser.replace_template_values(template_path, job_dict, save=True, output_file=output_path)

            # Save another copy for records
            # Grab request name
            # Save another copy for records, including request name in filename
            request_name = job_dict.get("REQUEST_NAME", "unnamed_request")
            template_name = Path(template_path).stem
            template_ext = Path(template_path).suffix

            # Create a unique filename: <template>_<request>.ext
            outfile_name = f"{template_name}_{request_name}{template_ext}"
            outfile = timestamp_dir / outfile_name

            parser.replace_template_values(template_path, job_dict, save=True, output_file=outfile)

        if not test:
            submit_crab_job(template_files["/uscms_data/d3/delossan/CMSSW_13_0_13/src/crab_submission_helper/data/templates/crab_template.py"],
                            run_directory=run_directory)  # uncomment and implement your submission logic

def submit_crab_job(config_file_path:str, run_directory:Optional[str]=None)->str:
    output = subprocess.run(f"crab submit {config_file_path}",
                            shell=True,
                            capture_output=True,
                            cwd=run_directory,
                            text=True)

    # Verify proper submission of task
    # Check for errors in execution
    if output.returncode != 0:
        logger.error("❌ CRAB submission failed to execute.")
        logger.error("stderr: %s", output.stderr)
        logger.error("stdout: %s", output.stdout)
    else:
        output = output.stdout
        logger.debug(output)

        # Verify successful CRAB task submission
        if "Success:" in output or "Task submitted successfully" in output:
            logger.info("✅ CRAB task submitted successfully!")
        else:
            logger.error("⚠️ CRAB submission command ran, but no success message was found.")
            logger.error("Output was: %s", output)

    return output

def get_crab_status(crab_directory:str, run_directory:Optional[str]=None)->dict:
    output = subprocess.run(f"crab status --json {crab_directory}",
                            shell=True,
                            capture_output=True,
                            cwd=run_directory,
                            text=True).stdout
    task_status_dict = parser.status_parser(output)
    return task_status_dict

def get_crab_output_directory(crab_directory:str, run_directory:Optional[str]=None)->str:
    output = subprocess.run(f"crab getoutput --quantity=1 -d {crab_directory} --dump",
                            shell=True,
                            capture_output=True,
                            cwd=run_directory,
                            text=True).stdout
    # Parse output for LFN
    return path

def crab_resubmit(crab_directory:str, resubmit_options:Optional[dict]=None, run_directory:Optional[str]=None)->bool:
    # Start building the command
    crab_command = ["crab", "resubmit", "-d", crab_directory]

    # Add optional flags
    if resubmit_options:
        if "maxmemory" in resubmit_options:
            crab_command += ["--maxmemory=", str(resubmit_options["maxmemory"])]
        if "siteblacklist" in resubmit_options:
            crab_command += ["--siteblacklist=", ",".join(resubmit_options["siteblacklist"])
                             if isinstance(resubmit_options["siteblacklist"], list)
                             else str(resubmit_options["siteblacklist"])]
        if "sitewhitelist" in resubmit_options:
            crab_command += ["--sitewhitelist=", ",".join(resubmit_options["sitewhitelist"])
                             if isinstance(resubmit_options["sitewhitelist"], list)
                             else str(resubmit_options["sitewhitelist"])]

    # Run the command
    result = subprocess.run(crab_command, capture_output=True, text=True, cwd=run_directory)


    return result.returncode, crab_command

def grab_crab_directories(glob_pattern:str = "*", crab_directory:str="crab/")->list[str]:
    """
    Grab a list of the crab directories that can be used for grabbing the status of / resubmitting
    """
    BASE_DIR = Path(crab_directory)
    return list(BASE_DIR.glob(glob_pattern))

if __name__ == "__main__":

    template_files = {"data/templates/config_cfg_template.py" : "./config.py",
                      "data/templates/crab_template.py" : "./crab.py"}

    batch_submit_jobs("example_batch_submission.yaml", template_files, [gen.add_dataset, gen.add_request_name])
