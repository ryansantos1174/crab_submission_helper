import argparse
import os
import sys
import subprocess
from typing import Optional


class MissingInput(Exception):
    pass

def grab_output_files(directory:str, grab_skim_files=False, grab_hist_files=False, pattern:Optional[str]= None, antipattern:Optional[str]= None) -> list[str]:
    """
    Grab output files to process for merging

    directory: Path to output file directory. It's expected this directory contains subdirectories of the form
    0000, 0001, 0002, etc. 
    """

    if not (grab_skim_files or grab_hist_files):
        raise MissingInput("You need to set either grab_skim_files or grab_hist_files to True")
    
    subdirectories: list[str] = subprocess.run(["xrdfs", "root://cmseos.fnal.gov", "ls", directory], capture_output=True, text=True).stdout.splitlines()
    output_files: list[str] = []
    
    for subdir in subdirectories:
        files_to_check = subprocess.run(["xrdfs", "root://cmseos.fnal.gov", "ls", "-u", subdir], capture_output=True, text=True).stdout.splitlines()
        
        filter_condition = "skim" if grab_skim_files else "hist"

        # Check for antipatterns to avoid and patterns in files
        if pattern:
            if antipattern:
                output_files += [file for file in files_to_check if filter_condition in file and pattern in file and not antipattern in file]
            else:
                output_files += [file for file in files_to_check if filter_condition in file and pattern in file]
        else:
            if antipattern:
                output_files += [file for file in files_to_check if filter_condition in file and not antipattern in file]
            else:
                output_files += [file for file in files_to_check if filter_condition in file]

    return output_files

def merge(input_files:list[str], output_path:str):
    subprocess.run(["hadd","-f", "-O", "-j", "8",  output_path] + input_files, check=True)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='Crab File Merger',
                        description='Merge output files from crab jobs')

    # TODO: Add in ability to specify multiple input directories
    parser.add_argument('--skim', action='store_true')
    parser.add_argument('--hist', action='store_true')
    parser.add_argument('--pattern', default=None)
    parser.add_argument('--antipattern', default=None)
    parser.add_argument('directory_path')
    parser.add_argument('output_path', default='output.root')

    args = parser.parse_args()
    output_files = grab_output_files(args.directory_path, grab_hist_files=args.hist, grab_skim_files=args.skim,
                                     pattern=args.pattern, antipattern=args.antipattern)
    merge(output_files, args.output_path)

