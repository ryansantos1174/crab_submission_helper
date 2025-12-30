"""
Functions to generate values that are needed for the replacement
of templated values in the template files.

ie. Functions to generate the request name or functions
to gather the correct lumimask
"""
from typing import Any, Callable
import logging

import tomli

from . import config as conf

logger = logging.getLogger(__name__)

def missing_required_keys(dictionary: dict, required_keys: list[str]) -> list[str]:
    return [k for k in required_keys if k not in dictionary]

def add_skim_files(values:str):
    """
    Add path to txt file containing skim files to dictionary
    """
    required_keys = ["REQUEST_NAME"]
    if missing_required_keys(values, required_keys):
        logging.error("Missing REQUEST_NAME key. Make sure you run this generator after add_request_name().")
        raise KeyError("Missing required keys in values: REQUEST_NAME")

    #skim_file_path
    #return {"SKIM_FILE": skim_file_path}

def generate_template_values(
    input_values: dict[str, Any],
    generating_function: Callable[[dict[str, Any]], dict[str, Any]]
) -> dict[str, Any]:
    """
    Generate values based off the output of another function. For example,
    this is helpful when trying to fill in the request name for the template files.
    You would like to generate a request name programmatically instead of letting the user decide.

    Arguments:
    input_values - A dictionary of values that should be used in your generating function
    generating_function - A function that should take in a dictionary and output a dictionary
    """

    temp_dict = generating_function(input_values)
    return input_values | temp_dict

def add_lumi_mask(values: dict[str, Any]) -> dict[str, Any]:
    required_keys = ["YEAR"]

    # --- Validate required keys ---
    if missing_required_keys(values,required_keys):
        raise KeyError("Missing required keys in values")

    dataset_file = conf.PROJECT_ROOT / "configs" / "datasets.toml"

    with dataset_file.open("rb") as f:
        dataset_data = tomli.load(f)

    year = values["YEAR"]
    logger.debug("Selection Year: %s", year)
    lumi_mask = dataset_data[str(year)]["lumiMask"]
    logger.debug("Lumi Mask: %s", lumi_mask)
    return {"LUMIMASK": lumi_mask}

def add_request_name(values: dict[str, Any]) -> dict[str, Any]:
    """
    Generate the request name so it follows the following pattern:
    <Selection>_<Year><Era>_v<era version>_<dataset><dataset version>
    ie. ZtoTauToEleProbeTrk_2023C_v1_Muon0

    If there are multiple selections then they will also be added:
    ie. ZtoTauToEleProbeTrk_ZtoTauToEleProbeTrkWithFilter_2023C_v1_Muon0
    """
    # Ensure that the necessary values are inside of the values dictionary.
    # We need selections, year, era, and dataset version
    required_keys = ["SELECTION", "YEAR", "ERA", "ERA_VERSION", "DATASET_TYPE", "DATASET_VERSION"]

    print(f"{values=}")
    # --- Validate required keys ---
    if missing_required_keys(values, required_keys):
        logging.error(
            "Your selections are missing DATASET. Make sure that you have ran the add_dataset function "
            "before calling add_request_name!!!!"
        )
        raise KeyError("Missing required keys in values")

    # --- Normalize and extract values ---
    selections = values["SELECTION"]
    year = str(values["YEAR"])
    era = str(values["ERA"])
    era_version = str(values["ERA_VERSION"])
    dataset = str(values["DATASET_TYPE"])
    dataset_version = str(values["DATASET_VERSION"])

    # Ensure selections is a list
    if isinstance(selections, str):
        selections = [selections]
    elif not isinstance(selections, (list, tuple)):
        raise TypeError("SELECTION must be a string or a list/tuple of strings")

    # --- Build the request name ---
    selection_part = "_".join(selections)
    request_name = f"{selection_part}_{year}{era}_v{era_version}_{dataset}{dataset_version}"

    # --- Return new dictionary entries ---
    return {"REQUEST_NAME": request_name}

def add_dataset(values: dict[str, Any]) -> dict[str, Any]:
    required_keys = ["SELECTION", "YEAR", "ERA", "ERA_VERSION", "DATASET_VERSION"]

    print(values)
    print(required_keys)
    if missing_required_keys(values, required_keys):
        logging.error("Missing REQUEST_NAME key. Make sure you run this generator after add_request_name().")
        raise KeyError("Missing required keys in values: REQUEST_NAME")

    dataset_file = conf.PROJECT_ROOT / "configs" / "datasets.toml"
    selections_file = conf.PROJECT_ROOT / "configs" / "selections.toml"

    with selections_file.open("rb") as f:
        data = tomli.load(f)

    with dataset_file.open("rb") as f:
        dataset_data = tomli.load(f)

    print(dataset_data.keys())
    dataset_type = data[values["SELECTION"]]

    dataset = dataset_data[str(values['YEAR'])][values['ERA']]["v"+str(values['ERA_VERSION'])][dataset_type+str(values["DATASET_VERSION"])]

    print(f"{dataset=}")
    # This requires that only one dataset per task is used (which should always be the case anyways)
    return {"DATASET_TYPE" : dataset_type,
            "DATASET": list(dataset.values())[0]}


if __name__ == "__main__":
    ...
