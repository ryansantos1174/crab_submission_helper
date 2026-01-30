#!/usr/bin/env python3
from datetime import datetime
import re
from typing import Optional, Callable
from collections import defaultdict # Needed to setup empty dictionary that contains lists

import json
import logging
from pathlib import Path

import yaml
import pandas as pd


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

    logger.debug("Status dataframe columns: %s", list(df.columns))

    df["Retries"] = pd.to_numeric(df["Retries"], errors="coerce").fillna(0)
    # Flag jobs with more than 5 retries
    df["TooManyRetries"] = df["Retries"] > 5

    if "Error" in df.columns: 
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
    pattern = r"crab_(?P<selection>.*)_(?P<year>\d{4})(?P<era>[A-Z]*)_?(?P<version>v.*?)?_(?P<dataset>.*)"
    print("Task name: ", task_name)
    print(type(task_name))
    match = re.match(pattern, task_name)
    if match:
        return (match.group("selection"),
                match.group("year"),
                match.group("era"),
                match.group("version"),
                match.group("dataset"))
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

    with open(template_file_path, "r", encoding='utf-8') as f:
        text = f.read()


    def replace_var(match):
        key = match.group(1)  # extract variable name between __ __
        value = replacement.get(key, match.group(0))
        return repr(value) # replace if found, else keep original


    subbed_text = re.sub(template_pattern, replace_var, text)

    if save and output_file:
        with open(output_file, "w", encoding='utf-8') as outfile:
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

    return None, None, None, None

def parse_yaml(yaml_file_path:str) -> dict['str', ...]:
    with open(yaml_file_path, "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def group_files(input_file_list:list[str],
                matching_function:Callable[[list], dict[str, list[str]]])-> dict[str, list[str]]:
    """
     Group files together based off the output matching_function.

    input_file_list: List of files that you would like to sort
    matching_function:  Function that should take in a list of strings and group them together
                        returning a dictionary with a key describing the grouping and a value
                        that is a list of the groupings (ex. groupEven([1,2,3,4,5] -> {"odd" :[1,3,5], "even": [2,4]))
    """
    assert len(input_file_list) > 1, "Not enough input files to group properly!"
    grouped_files: list[list[str]] = matching_function(input_file_list)
    return grouped_files

def group_by_selection(input_paths:list[str]):
    """
    Group file names by the selection that was ran to produce them.

    Used for the disappearing tracks analysis where output files look like
    skim_TauTagPt55_2026_01_03_22h44m20s_999.root. This function would group based
    off of TauTagPt55 and any other unique selections that are there. 
    """

    grouped_files: dict[str, list[str]] = defaultdict(list) 
    i = 0
    for path in input_paths:
        if i == 0:
            print("Path: ", path)
        i+=1
        selection = path.rsplit('/', 1)[1].split('_')[1]
        grouped_files[selection].append(path)

    return grouped_files

    
