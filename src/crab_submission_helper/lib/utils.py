"""
Miscellaneous functions that are used to help write other code (ie. functions
that don't necessarily help with crab commands, parsing, notifications, or google sheet
functionality).
"""
from pathlib import Path

def grab_configuration_file(task_directory:str) -> Path:
    """
    For a given task, grab the configuration files that were used
    to submit the task.

    task_directory: Directory pointing to your crab task relative to the run
                    directory (ex. DisappTrks/BackgroundEstimation/test/)
    """
