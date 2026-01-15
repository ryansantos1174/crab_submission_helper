#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Optional, Callable
import subprocess
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class EOSHelper():
    eos_base_directory: Optional[str] = None

    def is_file(self, file_or_subdir:str)->bool:
        """
        Determine whether an object points to a subdirectory or file on EOS
        """
        # Stat -f returns 0 if the object is a file
        process = subprocess.run(
            f"eos root://cmseos.fnal.gov stat -f {file_or_subdir}",
            shell = True,
            capture_output=False
        )

        return process.returncode == 0


    def is_subdir(self, file_or_subdir:str)->bool:
        # Stat -d returns 0 if the object is a directory
        process = subprocess.run(
            f"eos root://cmseos.fnal.gov stat -d {file_or_subdir}",
            shell = True,
            capture_output=False
        )

        return process.returncode == 0


    def grab_files_and_subdirectories(self, directory:str) -> list[str]:
        """
        Grab list of files and subdirectories within a directory.

        directory: string that describes a directory. Either an absolute path on EOS
        or a directory relative to eos_base_directory if that is set.

        raises: CalledProcessError if directory cannot be found
        return: List of absolute paths of subdirectories/files
        """
        try: 
            process = subprocess.run(
                f"eos root://cmseos.fnal.gov find --xurl --maxdepth 1 {directory}",
                shell=True,
                capture_output=True,
                text=True,
                check=True)
        except subprocess.CalledProcessError as e:
            logger.error(
                "Failed to find files in %s\n"
                "Command: %s\n"
                "Return code: %s\n"
                "----- stdout -----\n%s\n"
                "----- stderr -----\n%s",
                directory,
                e.cmd,
                e.returncode,
                (e.stdout or "").strip(),
                (e.stderr or "").strip(),
            )
            return []

        return process.stdout.splitlines()

    def regex_filter(self, pattern: str) -> Callable[[str], bool]:
        compiled = re.compile(pattern)

        def _filter(file: str) -> bool:
            return bool(compiled.search(file))

        return _filter

    def filter_files(self, file_list:list[str], filter_function:Callable)->list[str]:
        """
        Apply regex pattern to filter out files

        return: list of files that pass regex filter
        """
        return [f for f in file_list if filter_function(f)]

    @staticmethod
    def remove_files(file_paths:list[str])->None:
        """
        file_paths: absolute paths to file locations on EOS
        """
        for path in file_paths: 
            result = subprocess.run(
                f'eos root://cmseos.fnal.gov rm {path}',
                shell=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                logger.error(f"Error while deleting file {path}")

    @staticmethod
    def copy_file(file_path:str, output_path:str)->None:
        """
        file_paths: absolute paths to file locations on EOS
        """
        result = subprocess.run(
            f'eos root://cmseos.fnal.gov cp {file_path} {output_path}',
            shell=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Error while deleting file {path}")
