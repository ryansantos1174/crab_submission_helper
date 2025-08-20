"""
These functions are intended to dynamically generate the submission files
needed for the DisappTrks analysis. The template files are stored inside of templates/ and the configuration options are
stored within config/
"""
from typing import Optional
import os

import tomli as tomllib
from jinja2 import Environment, FileSystemLoader

def generate_crab_template(template_file:str, config_file:str, year:int,
                    era:str, channel:str, crab_config:str, request_name:str,
                    version: Optional[str] = None,
                    template_dir:str="templates", config_dir:str="configs",
                    output_directory:str = "output_files"):
    """
    Fill in template file with data given

    This function is intended to generate the crab submission file
    """

    # Load TOML config
    with open(os.path.join(config_dir, config_file), "rb") as f:
        config = tomllib.load(f)

    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    print("config: ", config)
    era_cfg = config[year][era]

    if year == "2023":
        if not version:
            raise ValueError(f"Year {year} requires a version")
        print(f"{era_cfg=}")
        print(f"{version=}, {channel=}")
        dataset = era_cfg[version][channel]["dataset"]
    else:
        dataset = era_cfg[channel]["dataset"]

    print("Dataset:", dataset)
    # Render the template
    output = template.render(
        year=year,
        era=era,
        config=crab_config,
        version=version,
        channel=channel,
        input_dataset=dataset,
        request_name=request_name
    )

    # Write to final Python script
    if version:
        output_file = f"crab_{year}_{era}_{version}_{channel}.py"
    else:
        output_file = f"crab_{year}_{era}_{channel}.py"
    with open(os.path.join(output_directory, output_file), "w") as f:
        f.write(output)
    return output_file

def generate_selection_template(template_file:str, config_file:str, selection:str, output_file:str = "test.py", template_dir:str = "templates", config_directory:str = "configs"):
    """
    This function is intended to generate the selections file that controls what selection you want to process
    """
    with open(os.path.join(config_directory, config_file), "rb") as f:
        config_file = tomllib.load(f)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    config = config_file[selection]

    zipped = zip(
        config["channels"],
        config["hist_sets"],
        config["weights"],
        config["scale_factor_producers"],
        config["collection_maps"],
        config["producers"],
        config["ignore_skimmed_collections"],
        config["force_non_empty_skim"])

    output = template.render(
        zipped=zipped)

    with open(output_file, "w") as f:
        f.write(output)

def generate_config_file(template_file:str, output_file_name:str, selection_file:str,
                         year:int, era:str,
                         isRealData:bool = True, applyPUReweighting:bool=False,
                         applyISRReweighting:bool = False,
                         applyTriggerReweighting:bool = False,
                         applyMissingHitsCorrections:bool = False,
                         runMETFilters:bool = False,
                         input_files:Optional[list[str]] = None,
                         lumis_to_process:Optional[list[str]] = None,
                         run_local:bool = False,
                         template_dir:str="templates"):
    """
    Generate the file that contains the customize() function which defines combines all inputs to CMSSW framework
    """
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    output = template.render(
        config_file_path = selection_file,
        year=year,
        era=era,
        run_local=run_local,
        isRealData = isRealData,
        applyPUReweighting = applyPUReweighting,
        applyISRReweighting = applyISRReweighting,
        applyTriggerReweighting = applyTriggerReweighting,
        applyMissingHitsCorrections = applyMissingHitsCorrections,
        runMETFilters = runMETFilters,
        input_files = input_files,
        lumis_to_process = lumis_to_process
    )
    with open(output_file_name, "w") as f:
        f.write(output)

def generate_submission_script(template_file:str, output_file_name:str,
                               job_descriptions:list[dict], template_dir:str='templates'):
    """
    Create bash script to submit all jobs with a single command

    job_descriptions: A dictionary with key config_name that contains the crab config_name
    """
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    script = template.render(jobs=job_descriptions)

    with open(output_file_name, "w") as f:
        f.write(script)




if __name__ == "__main__":
    CONFIG_TEMPLATE = "config_cfg.py.j2"
    SELECTION_TEMPLATE = "selections.py.j2"
    SELECTION_CONFIG_FILE = "selections.toml"

    # Setup jobs
    # NOTE: The current the way the code is set up we should only be runnining one selection at a time
    submission_description = [{"year": "2022", "era": "C", "channel": "Tau",
                               "request_name": "TauTagPt55_SingleMuonTrigger_2022C",
                               "config_file_output_name": "TauTagPt55_2022C_config.py"},
                            {"year": "2022", "era": "D", "channel": "Tau",
                               "request_name": "TauTagPt55_SingleMuonTrigger_2022D",
                               "config_file_output_name": "TauTagPt55_2022D_config.py"},
                            {"year": "2022", "era": "E", "channel": "Tau",
                               "request_name": "TauTagPt55_SingleMuonTrigger_2022E",
                               "config_file_output_name": "TauTagPt55_2022E_config.py"},
                            {"year": "2022", "era": "G", "channel": "Tau",
                               "request_name": "TauTagPt55_SingleMuonTrigger_2022G",
                               "config_file_output_name": "TauTagPt55_2022G_config.py"}
                              ]

    selection_file_name = "TauTagPt55_selections.py"
    selection = "TauTagPt55"
    generate_selection_template("selections.py.j2", "selections.toml", selection,
                                selection_file_name)
    for description in submission_description:
        print(description)
        generate_crab_template("crab_template.py.j2", "job_options.toml", year=description["year"],
                            era=description["era"], channel=description["channel"],
                            crab_config=description["config_file_output_name"],
                            request_name=description["request_name"])

        generate_config_file(template_file="config_cfg.py.j2",
                            output_file_name=description["config_file_output_name"],
                            selection_file=selection_file_name,
                            year=description["year"], era=description["era"], run_local=False)


    job_description = {"config_name" : name["config_file_output_name"] for name in submission_description}
    generate_submission_script("submission_script.sh.j2", description["request_name"]+"_submission.sh",
                                job_descriptions=job_description)
