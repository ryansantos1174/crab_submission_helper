#!/usr/bin/env python3
from pathlib import Path
from crab_submission_helper.lib.crab_helper import CrabHelper
import crab_submission_helper.lib.parse_helper as ph
import crab_submission_helper.lib.generator as gen
from crab_submission_helper.lib.utils import PROJECT_ROOT
import logging

run_directory:Path = Path('')
crab_directory:Path = Path('')

batch_file:str= ... # Path to batch_file
template_directory_path = Path(__file__).parent.parent / "src" / "crab_submission_helper" / "data" / "templates"
template_config_file = PROJECT_ROOT / "configs" / "templates.yml"

ch = CrabHelper()

template_files = ph.parse_template_files(
    template_directory_path, run_directory, template_config_file
)

def add_skim_files_no_directory(input_values: dict):
    if isinstance(input_values["NLAYERS"], str):
        input_values["NLAYERS"] = True if input_values["NLAYERS"].lower() == "true" else False

    if not isinstance(input_values["NLAYERS"], bool):
        raise TypeError("Unable to cast NLAYERS variable as a bool")

    if not input_values["NLAYERS"]:
        return {}

    required_keys = ["REQUEST_NAME", "OUTPUT_DIRECTORY", "SELECTION"]
    if gen.missing_required_keys(input_values, required_keys):
        logging.error("Missing REQUEST_NAME key. Make sure you run this generator after add_request_name().")
        raise KeyError("Missing required keys in values: REQUEST_NAME")

    output_directory = input_values["OUTPUT_DIRECTORY"]
    matched_files = ch.find_files(hist_or_skim = 'skim', directory=output_directory)

    grouped_files: dict[str, list[str]] = ph.group_files(matched_files, ph.group_by_selection)

    selection = input_values["SELECTION"]

    skim_file_list = grouped_files[selection]

    skim_file = run_directory / f"{input_values['REQUEST_NAME']}_skim_files.txt"
    skim_file.write_text("\n".join(skim_file_list))

    return {"SKIM_FILE": str(skim_file.absolute())}






generating_functions = [
    gen.add_dataset,
    gen.add_request_name,
    gen.add_lumi_mask,
    ch.add_skim_files_no_directory,
]

ch.batch_submit_jobs(batch_file, template_files, test=True)
