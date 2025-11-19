#!/usr/bin/env python3
from datetime import datetime
import re
from typing import Optional
import yaml
import pandas as pd
import json
import logging
from pathlib import Path
from . import config as conf


logger = logging.getLogger(__name__)

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

def parse_task_name(task_name:str)-> tuple:
    """
    Parse information about the year, era, and selection that a task was ran with

    Especially important for recovery tasks where you may want to submit a task
    but don't want to have to recreate an entry by hand in the yaml file
    """
    pattern ="crab_(?P<selection>.*)_(?P<year>\d{4})(?P<era>[A-Z])_?(?P<version>v\d)?_(?P<dataset>NLayers|EGamma\d|Muon\d)"
    match = re.match(pattern, task_name)
    if match:
        return (match.group("selection"),
                match.group("year"),
                match.group("era"),
                match.group("version"),
                match.group("dataset"))
    else:
        raise ValueError("Unable to parse data from task name")


def parse_template_files(template_directory:Path, run_directory:Path,
                        template_yaml_file:Path) -> dict:
    """
    Parse yaml file for the template files that you would like to process
    and their corresponding output positions

    Args:
        template_directory: Path object where template files are stored
        run_directory: Path object where the cmsRun command will be ran from

    Returns:
        dict: Dictionary with keys being the template file name relative to the template
              directory and values being the output destination
    """

    config = parse_yaml(template_yaml_file)
    entries = config["templates"]

    output_dict = {
        (Path(template_directory) / entry["input"]).resolve():
        (Path(run_directory) / entry["output"]).resolve()
        for entry in entries
    }
    logger.debug("Template file path dictionary %s", output_dict)

    return output_dict

def grab_submission_time(status_df:pd.DataFrame)-> datetime:
    ...


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
        value = replacement.get(key, match.group(0))
        return repr(value) # replace if found, else keep original


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
