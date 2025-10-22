#!/usr/bin/env python3
from datetime import datetime
import re
from typing import Optional
import yaml
import pandas as pd
import json

def status_parser(crab_status_output: str) -> pd.DataFrame:
    """
    Grab the status of the jobs from the "crab status --json".
    """
    # These error codes mean job is taking up too much resources and a resubmit is unlikely to fix the issue
    UNRECOVERABLE_EXIT_CODES = {50660, 50661, 50662}
    output = crab_status_output.strip()

    # Look for json object boundaries
    start = output.find('{')
    end = output.rfind('}')
    if start == -1 or end == -1 or end <= start:
        if "Files are purged" in output:
            return pd.DataFrame([{"State": "purged", "message": "Files purged from Grid scheduler"}])
        else:
            return pd.DataFrame([{"State": "unknown", "message": "No JSON found"}])

    json_str = output[start:end + 1]

    # Try parsing the JSON section
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return pd.DataFrame([{"State": "invalid", "message": str(e)}])

    # Build DataFrame
    df = pd.DataFrame.from_dict(data, orient="index").reset_index()
    df.rename(columns={"index": "job_id"}, inplace=True)

    df["Retries"] = pd.to_numeric(df["Retries"], errors="coerce").fillna(0)
    # Flag jobs with more than 5 retries
    df["TooManyRetries"] = df["Retries"] > 5
    df["HasUnrecoverableError"] = df["Error"].apply(
        lambda x: x[0] in UNRECOVERABLE_EXIT_CODES if isinstance(x, list) and x else False
    )

    return df


def grab_submission_time(status_df:pd.DataFrame)-> datetime:


def replace_template_values(template_file_path:str, replacement:dict,
                            save:bool =True, output_file:Optional[str]=None)->None:
    """
    Replace values of the form __VALUE__ inside of file with
    values inside a dictionary of the same name.

    ex.
    if __SKIM_FILE__ were in a file,  {"SKIM_FILE": test} would replace
    __SKIM_FILE__ with test.
    """

    # Uppercase keys in replacement to keep readability in yaml
    replacement = {k.upper(): v for k, v in replacement.items()}

    template_pattern = r"__([A-Z0-9_]+)__"

    with open(template_file_path, "r") as f:
        text = f.read()


    def replace_var(match):
        key = match.group(1)  # extract variable name between __ __
        return str(replacement.get(key, match.group(0)))  # replace if found, else keep original

    subbed_text = re.sub(template_pattern, replace_var, text)

    if save and output_file:
        with open(output_file, "w") as outfile:
            outfile.write(subbed_text)

    elif save and not output_file:
        logger.error("You cannot save your configuration file without first setting a output file!")

    elif output_file and not save:
        logger.error("You have output_file set but not save. Did you mean to save the configuration file?")

def parse_crab_task(task_name:str)->Optional[tuple[str,...]]:
    # Get last directory
    task = task_name.split("/")[-1]
    # Get rid of "crab_" at the beginning of file path
    task = "_".join(task.split("_")[1:])
    match = re.search(r'([a-zA-Z]*\d*)_(\d{4}[A-Z])_(v\d)_(?:Muon|EGamma)(\d)', task)
    if match:
        selection = match.group(1)
        era = match.group(2)  # '2023C'
        version = match.group(3)  # 'v1'
        dataset_version = match.group(4)
        return selection, era, version, dataset_version
    else:
        return None, None, None, None

def parse_yaml(yaml_file_path:str) -> dict['str', ...]:
    with open(yaml_file_path, "r") as f:
        data = yaml.safe_load(f)
    return data




if __name__ == "__main__":
    replacement = {"SKIM_FILE": "test.py",
                   "DATASET" : "ahhhh",
                   "REQUESTNAME" : "sldkjfa"}

    replace_template_values("crab_2022_Tau_template.py", replacement)
