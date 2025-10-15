#!/usr/bin/env python3
import subprocess
import glob
import lib.parse_helper as parser
from typing import Optional
from pathlib import Path

def submit_crab_job(config_file_path:str, run_directory:Optional[str]=None)->str:
    output = subprocess.run(f"crab submit {config_file_path}",
                            shell=True,
                            capture_output=True,
                            cwd=run_directory,
                            text=True).stdout

    # Verify proper submission of task
    ...

    return output

def get_crab_status(crab_directory:str, run_directory:Optional[str]=None)->dict:
    output = subprocess.run(f"crab status {crab_directory}",
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
    ...
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
