import argparse
import os
import sys
import subprocess


class MissingInput(Exception):
    pass

def grab_output_files(directory:str, grab_skim_files=False, grab_hist_files=False)-> list[str]:
    """
    Grab output files to process for merging

    directory: Path to output file directory. It's expected this directory contains subdirectories of the form
    0000, 0001, 0002, etc. 
    """

    if not (grab_skim_files or grab_hist_files):
        raise MissingInput("You need to set either grab_skim_files or grab_hist_files to True")
    

    subdirectories:list[str] = subprocess.run(["xrdfs", "root://cmseos.fnal.gov", "ls", directory], capture_output=True, text=True).stdout.splitlines()
    output_files:list[str] = []
    for subdir in subdirectories:
        files_to_check = subprocess.run(["xrdfs", "root://cmseos.fnal.gov", "ls", "-u", subdir], capture_output=True, text=True).stdout.splitlines()
        if grab_skim_files:
            output_files += [file for file in files_to_check if "skim" in file]
        else:
            output_files += [file for file in files_to_check if "hist" in file]
    return output_files

def merge(input_files:list[str], output_path:str):
    subprocess.run(["hadd", "-O", "-j", "8",  output_path] + input_files, check=True)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='Crab File Merger',
                        description='Merge output files from crab jobs')

    # TODO: Add in ability to specify multiple input directories
    parser.add_argument('--skim', action='store_true')
    parser.add_argument('--hist', action='store_true')
    parser.add_argument('output_path', default='output.root')
    parser.add_argument('directory_path')

    args = parser.parse_args() 
    
    output_files = grab_output_files(args.directory_path, grab_hist_files=args.hist, grab_skim_files=args.skim)
    merge(output_files, args.output_path)

