#!/usr/bin/env python3
import re
from typing import Optional

def status_parser(crab_status_output:str)->dict:
    # Search for failed and finished optionally so that if either are not there the
    # search doesn't fail
    failed_pattern_search = r".*failed\s+\d.*%.*"
    finished_pattern_search = r".*finished\s+\d.*%.*"

    failed_match = re.search(failed_pattern_search, crab_status_output)
    finished_match = re.search(finished_pattern_search, crab_status_output)

    return {"Failed": bool(failed_match), "Finished" : bool(finished_match)}

def replace_template_values(template_file_path:str, replacement:dict)->None:
    """
    Replace values of the form __VALUE__ inside of file with
    values inside a dictionary of the same name.

    ex.
    if __SKIM_FILE__ were in a file,  {"SKIM_FILE": test} would replace
    __SKIM_FILE__ with test.
    """
    template_pattern = r"__([A-Z0-9_]+)__"

    with open(template_file_path, "r") as f:
        text = f.read()

    def replace_var(match):
        key = match.group(1)  # extract variable name between __ __
        return replacement.get(key, match.group(0))  # replace if found, else keep original

    subbed_text = re.sub(template_pattern, replace_var, text)
def parse_crab_task(task_name:str)->Optional[tuple(str)]:
    # Get rid of "crab_" at the beginning of file path
    task = "_".join(task_name.split("_")[1:])
    match = re.search(r'_(\d{4}[A-Z])_(v\d+)_(?:Muon|EGamma)(v\d)', task)
    if match:
        selection = match.group(0)
        era = match.group(1)  # '2023C'
        version = match.group(2)  # 'v1'
        dataset_version = match.group(3)
        return selection, year, version, dataset_version
    else:
        return None, None, None, None

if __name__ == "__main__":
    replacement = {"SKIM_FILE": "test.py",
                   "DATASET" : "ahhhh",
                   "REQUESTNAME" : "sldkjfa"}

    replace_template_values("crab_2022_Tau_template.py", replacement)
