"""
Functions to interact directly with the crab command
ie. submitting jobs and getting status/log information
"""

import subprocess
import datetime
from dataclasses import dataclass
import logging
from typing import Optional, Union, Callable, Dict
from pathlib import Path, PurePosixPath
import re
import tempfile

from . import parse_helper as parser
from . import generators as gen
from . import config as conf

logger = logging.getLogger(__name__)

@dataclass
class CrabHelper():
    crab_directory: Path | None = None
    run_directory: Path | None = None

    def batch_submit_jobs(self,
        batch_file: str,
        template_files: Dict[str, str],
        generating_functions: Union[Callable, list[Callable], None] = [
            gen.add_dataset,
            gen.add_request_name,
            gen.add_lumi_mask,
            gen.add_skim_files
        ],
        test: bool = False,
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
                    gen.generate_template_values(job_dict, func)
                    for job_dict in job_replacements
                ]
        print(job_replacements)
        logging.info("Processed %s job replacements.", len(job_replacements))

        # Save templates for each job
        timestamp_dir = (
            conf.PROJECT_ROOT
            / "src"
            / "crab_submission_helper"
            / "data"
            / "generated"
            / datetime.datetime.now().strftime("%Y%m%d_%H%M")
        )
        timestamp_dir.mkdir(parents=True, exist_ok=True)
        for job_dict in job_replacements:
            for template_path, output_path in template_files.items():
                # Save one copy for use in job
                parser.replace_template_values(
                    template_path, job_dict, save=True, output_file=output_path
                )

                if not test:
                    # Save another copy for records, including request name in filename
                    request_name = job_dict.get("REQUEST_NAME", "unnamed_request")
                    template_name = Path(template_path).stem
                    template_ext = Path(template_path).suffix

                    # Create a unique filename: <template>_<request>.ext
                    outfile_name = f"{template_name}_{request_name}{template_ext}"
                    outfile = timestamp_dir / outfile_name

                    parser.replace_template_values(
                        template_path, job_dict, save=True, output_file=outfile
                    )

            if not test:
                # Find entry that corresponds to crab configuration file
                # TODO: Probably is a better way to do this instead of looking for a string inside of the dictionary keys.
                key = next(
                    k for k in template_files
                    if "crab_template.py" in k.name
                )
                self.submit_crab_job(template_files[key])  # uncomment and implement your submission logic


    def submit_crab_job(self, config_file_path: str) -> Optional(str):
        try:
            output = subprocess.run(
                f"crab submit {config_file_path}",
                shell=True,
                capture_output=True,
                cwd=self.run_directory,
                text=True,
                check=True
            )

            # Verify proper submission of task
            # Check for errors in execution
            output = output.stdout
            logger.debug(output)

            # Verify successful CRAB task submission
            if "Success:" in output or "Task submitted successfully" in output:
                logger.info("✅ CRAB task submitted successfully!")
            else:
                logger.error(
                    "⚠️ CRAB submission command ran, but no success message was found."
                )
                logger.error("Output was: %s", output)
            return output
        except subprocess.CalledProcessError as e:
            logger.error(
                "CRAB submission failed\n"
                "Command: %s\n"
                "Return code: %s\n"
                "----- stdout -----\n%s\n"
                "----- stderr -----\n%s",
                e.cmd,
                e.returncode,
                (e.stdout or "").strip(),
                (e.stderr or "").strip(),
            )

    def get_crab_status(self, task_directory: str) -> dict:
        try:
            output = subprocess.run(
                f"crab status --json {task_directory}",
                shell=True,
                capture_output=True,
                cwd=self.run_directory,
                text=True,
                check=True
            ).stdout
        except subprocess.CalledProcessError as e:
            logger.error(
                "Grabbing task status failed\n"
                "Command: %s\n"
                "Return code: %s\n"
                "----- stdout -----\n%s\n"
                "----- stderr -----\n%s",
                e.cmd,
                e.returncode,
                (e.stdout or "").strip(),
                (e.stderr or "").strip(),
            )

        task_status_dict = parser.status_parser(output)
        return task_status_dict


    def get_crab_output_directory(self,
        task_directory: str
    ) -> str:
        output = subprocess.run(
            f"crab getoutput --quantity=1 -d {task_directory} --dump --jobids=1",
            shell=True,
            capture_output=True,
            cwd=self.run_directory,
            text=True,
        )

        if output.returncode != 0:
            logger.error("Not able to find output directory!")
            return "Not Found!"



        # NOTE: Since we this regex looks for /store/group/lpclonglived/DisappTrks if we
        # eventually change storage locations, this will break.
        pattern = re.compile(r"/store/group/lpclonglived/DisappTrks/[^/]+/[^/]+/")
        match = pattern.search(output.stdout)

        if match:
            logger.debug("Output Directory: %s", match.group(0))
        else:
            logger.debug("No match found. Command output: %s", output.stdout)
            return "Not Found!"
        # Parse output for LFN
        return match.group(0)


    def crab_resubmit(
        self,
        task_directory: str,
        resubmit_options: Optional[dict] = None,
    ) -> bool:
        # Start building the command
        crab_command = ["crab", "resubmit", "-d", task_directory]

        # Add optional flags
        if resubmit_options:
            if "maxmemory" in resubmit_options:
                crab_command += [f"--maxmemory={resubmit_options['maxmemory']}"]
            if "siteblacklist" in resubmit_options:
                crab_command += [
                    "--siteblacklist=",
                    (
                        ",".join(resubmit_options["siteblacklist"])
                        if isinstance(resubmit_options["siteblacklist"], list)
                        else str(resubmit_options["siteblacklist"])
                    ),
                ]
            if "sitewhitelist" in resubmit_options:
                crab_command += [
                    "--sitewhitelist=",
                    (
                        ",".join(resubmit_options["sitewhitelist"])
                        if isinstance(resubmit_options["sitewhitelist"], list)
                        else str(resubmit_options["sitewhitelist"])
                    ),
                ]

        # Run the command
        result = subprocess.run(
            crab_command, capture_output=True, text=True, cwd=self.run_directory, check=False
        )

        return result.returncode, result.args


    def grab_crab_directories(self,
        glob_pattern: str = "*"
    ) -> list[str]:
        """
        Grab a list of the crab task directories that can be used for grabbing the status of / resubmitting
        """
        assert self.crab_directory is not None, "crab_directory was not initialized with CrabHelper!"

        base_dir = self.crab_directory
        return list(base_dir.glob(glob_pattern))


    def find_files(self, hist_or_skim: str, directory: str)->list[str]:
        hist_pattern = "hist.*.root"
        skim_pattern = "skim.*.root"
        if hist_or_skim == "hist":
            regex = hist_pattern
        elif hist_or_skim == "skim":
            regex = skim_pattern
        else:
            logger.error(
                "Generalized regex is not available yet. You must pass 'hist' or 'skim'."
            )
            return

        try:
            output = subprocess.run(
                f'eos root://cmseos.fnal.gov find --xurl --name "{regex}" "{directory}"',
                shell=True,
                capture_output=True,
                text=True,
                check=True
            ).stdout
        except subprocess.CalledProcessError as e:
            logger.error(
                "Failed to find file crab task output files!"
                "Command: %s\n"
                "Return code: %s\n"
                "----- stdout -----\n%s\n"
                "----- stderr -----\n%s",
                e.cmd,
                e.returncode,
                (e.stdout or "").strip(),
                (e.stderr or "").strip(),
            )

        # Create an output file with file paths for ease-of-use with hadd and edmCopyPickMerge
        with open("listOfInputFiles.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(output.splitlines()))  # Write each entry on a new line

        return output.splitlines()

    def merge_files(self, files_to_be_merged:list[str], output_file: str, is_skim_file: bool) -> tuple[str,str,int]:

        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            tmp.write("\n".join(files_to_be_merged))
            tmp.close()

            # Merging skim files requires edmCopyPickMerge and hist files can just be merged with hadd
            if is_skim_file:
                command = f"edmCopyPickMerge inputFiles_load={tmp.name} outputFile={output_file}"
            else:
                command = f"hadd -O -j 8 {output_file} @{tmp.name}"
            try:
                output = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True
                )

            except subprocess.CalledProcessError as e:
                logger.error(
                    "Failed to hadd output files together!"
                    "Command: %s\n"
                    "Return code: %s\n"
                    "----- stdout -----\n%s\n"
                    "----- stderr -----\n%s",
                    e.cmd,
                    e.returncode,
                    (e.stdout or "").strip(),
                    (e.stderr or "").strip(),
                )
            logger.debug(output.args)
            logger.debug(output)


        return output.stdout, output.stderr, output.returncode


    def copy_to_eos(self, target_path:str, file_to_copy:str) -> None:
        """
        Function to copy files to EOS space

        target_path: Path on EOS where you would like to write your files (ie. don't prepend root://cmseos.fnal.gov//)
        file_to_copy: File you would like to copy
        """

        command = f"xrdcp {file_to_copy} root://cmseos.fnal.gov/{target_path}"

        output = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )

        if output.returncode != 0:
            logger.error("Unable to copy file to EOS space."
                        "Return code was %s", output.returncode)
            return

        logger.info("Successfully copied %s to %s", file_to_copy, target_path)
        

    def cleanup_intermediate_files(self, target_path:str)->None:
        """
        Clear up intermediate skim and hist files produced by crab

        Common directory path on EOS is something like:
        /store/group/lpclonglived/DisappTrks/Muon0/ZtoTauToEleProbeTrk_2024C_v1_EGamma1/20260203_133411/0000

        This command will remove all directories inside ZtoTauToEleProbeTrk_2024C_v1_EGamma1, this will include the log
        directories.

        This command should be used with extreme caution. There's no way to recover files after deletion.

        target_path: Path to directory containing the intermediate files that you would like
                    to remove (ex. /store/group/lpclonglived/DisappTrks/Muon0/ZtoTauToEleProbeTrk_2024C_v1_EGamma1/)
        """
        try:
            output = subprocess.run(
                f'eos root://cmseos.fnal.gov ls {target_path}',
                shell= True,
                capture_output=True,
                text = True,
                check=True
            )

            subdirs_and_files:list[str] = output.stdout.rstrip().split('\n')

            # This assumes that the only files will be root files
            subdirectories = [path for path in subdirs_and_files if not path.endswith(".root")]

            # Using PurePosixPath to avoid issues with trailing \ with direct string
            # concatenation. The path is also on EOS so want to deter/avoid attempts to actually
            # access the file since this needs to be done with eos specific commands
            full_subdirectory_path:list[str] = [str(PurePosixPath(target_path) / subdir) for subdir in subdirectories]

        except CalledProcessError:
            logger.error("Failed to grab subdirectories. Exiting.")
            return

        except Exception as e:
            logger.error("Unexpected error: %s", e)
            return

        try:
            # Confirm deletion before deleting subdirectories
            logger.warning(
                "The following EOS paths will be permanently deleted:\n%s",
                "\n".join(f"  {p}" for p in full_subdirectory_path),
            )

            response = input("Type 'yes' to confirm deletion: ").strip()

            if response.lower() != 'yes':
                logger.info("Aborting deletion of directories")
                return

            for subdirectory in full_subdirectory_path:
                output = subprocess.run(
                    f'eos root://cmseos.fnal.gov rm -r {subdirectory}',
                    shell=True,
                    capture_output=False,
                    check=True
                )

        except CalledProcessError:
            logger.error("Failed to remove files. Exiting.")
