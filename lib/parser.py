#!/usr/bin/env python3
import re

def status_parser(crab_status_output:str)->dict:
    # Search for failed and finished optionally so that if either are not there the
    # search doesn't fail
    failed_pattern_search = r".*failed\s+\d.*%.*"
    finished_pattern_search = r".*finished\s+\d.*%.*"

    failed_match = re.search(failed_pattern_search, crab_status_output)
    finished_match = re.search(finished_pattern_search, crab_status_output)

    return {"Failed": bool(failed_match), "Finished" : bool(finished_match)}

def replace_template_values(template_file_path:str, replacement:dict)->None:
    template_pattern = r"__([A-Z0-9_]+)__"

    with open(template_file_path, "r") as f:
        text = f.read()

    def replace_var(match):
        key = match.group(1)  # extract variable name between __ __
        print(key)
        return replacement.get(key, match.group(0))  # replace if found, else keep original

    subbed_text = re.sub(template_pattern, replace_var, text)
    print(subbed_text)

if __name__ == "__main__":
    replacement = {"SKIM_FILE": "test.py",
                   "DATASET" : "ahhhh",
                   "REQUESTNAME" : "sldkjfa"}
    replace_template_values("crab_2022_Tau_template.py", replacement)
