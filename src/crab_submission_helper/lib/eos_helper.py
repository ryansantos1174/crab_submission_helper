#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class EOSHelper():
    eos_base_directory: Optional[str] = None

    def is_file(self, file_or_subdir:str)->bool:
        """
        Determine whether an object points to a subdirectory or file
        """
        ...

    def is_subdir(self, file_or_subdir:str)->bool:
        ...

    def grab_files_and_subdirectories(self, directory:str) -> list[str]:
        """
        Grab list of files and subdirectories within a directory.

        directory: string that describes a directory. Either an absolute path on EOS
        or a directory relative to eos_base_directory if that is set.

        raises: CalledProcessError if directory cannot be found
        return: List of absolute paths of subdirectories/files
        """

    def filter_files(self, file_list:list[str], filter_function:Callable)->list[str]:
        """
        Apply regex pattern to filter out files

        return: list of files that pass regex filter
        """
        return [f for f in file_list if filter_function(f)]
