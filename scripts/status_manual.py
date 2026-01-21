#!/usr/bin/env python3
"""
Grab status of a task manually (ie. specify a list of task directories) instead
of automatically looping through all subdirectories
"""
from pathlib import Path

from crab_submission_helper.lib.crab_helper import CrabHelper

crab_directory = Path(...)
run_directory = Path(...)

ch = CrabHelper(crab_directory = crab_directory, run_directory=run_directory)

# List of tasks relative to the crab directory
list_of_tasks = []

for task in list_of_tasks:
    df = ch.get_crab_status(task)
    print(df)
