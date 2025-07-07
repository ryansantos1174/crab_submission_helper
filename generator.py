from typing import Optional
import os

import tomli as tomllib
from jinja2 import Environment, FileSystemLoader

def render_crab_template(template_file:str, config_file:str, year:int,
                    era:str, channel:str,
                    version: Optional[str] = None, request_name: Optional[str] = None,
                    template_dir:str="templates"):
    """
    Fill in template file with data given
    """

    # Load TOML config
    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    print(config)
    print(year)
    print(era)
    era_cfg = config[year][era]

    if year == "2023":
        if not version:
            raise ValueError(f"Year {year} requires a version")
        dataset = era_cfg[version][channel]["dataset"]
    else:
        dataset = era_cfg[channel]["dataset"]

    print("Dataset:", dataset)
    # Render the template
    output = template.render(
        year=year,
        era=era,
        version=version,
        channel=channel,
        input_dataset=dataset,
        request_name=request_name
    )

    # Write to final Python script
    output_file = f"generated_{year}_{era}_{version}_{channel}.py"
    with open(output_file, "w") as f:
        f.write(output)

    print(f"Wrote {output_file}")
def render_selection_template(template_file:str, config_file:str, selection:str, output_file:str = "test.py", template_dir:str = "templates", config_directory:str = "configs"):

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
        
    

    
if __name__ == "__main__":
    render_selection_template("selections.py.j2", "selections.toml", "TauTagPt55")
