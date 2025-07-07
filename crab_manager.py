import subprocess
import textwrap
import sys
import os
from typing import Optional
import requests
import json
import argparse

import pandas as pd

import generator as gen

class CrabHandler:
    bad_exit_codes: tuple = 50660
    site_chances: int = 5

    resubmit_jobs: dict[int, dict] = None
    directories: Optional[list[str]] = None

    def crab_status(self, crab_directory: str) -> pd.DataFrame:
        # Submit crab status command on given crab directory
        output = subprocess.run(
            f"crab status -d {crab_directory} --json",
            shell=True,
            capture_output=True,
            text=True,
        ).stdout

        start = output.find("{")
        stop = output.find("Log")
        # Remove last log file line and the head of the file
        output = output[start:stop]

        return pd.read_json(output).transpose()

    def get_failed_job_ids(self, submitted_jobs: pd.DataFrame) -> pd.DataFrame:
        failed_ids = submitted_jobs[submitted_jobs["State"] == "failed"][
            ["JobIds", "SiteHistory"]
        ]
        failed_ids["LatestJobId"] = failed_ids["JobIds"].apply(lambda x: x[-1])
        failed_ids["LatestSite"] = failed_ids["SiteHistory"].apply(lambda x: x[-1])

        #self.resubmit_jobs = {key: {} for key in list(latest_failed_ids)}

        return failed_ids[["LatestJobId", "LatestSite"]]

    def check_location(self, submitted_jobs: pd.DataFrame):
        sites = submitted_jobs[["SiteHistory", "JobIds"]].value_counts().to_dict()
        for (site, job_id), count in sites.items():
            if count >= self.site_chances:
                if job_id not in self.resubmit_jobs:
                    self.resubmit_jobs[job_id] = {}
                self.resubmit_jobs[job_id]["SiteBlacklist"] = site

    def check_error(self): ...

    @staticmethod
    def process_failed_lumis_file(failed_lumis_file:str)->list[str]:
        with open(failed_lumis_file) as f:
            lumi_dict = json.load(f)

        ranges = []
        for run, ranges_list in lumi_dict.items():
            for lumi_start, lumi_end in ranges_list:
                if lumi_start == lumi_end:
                    ranges.append(f"{run}:{lumi_start}")
                else:
                    ranges.append(f"{run}:{lumi_start}-{run}:{lumi_end}")
        return ranges

    def grab_failed_lumis_and_files(self, crab_directory: str, testing=False)-> dict[str, str]:
        # Run Crab submit
        if not testing:
            subprocess.run(f"crab report -d {crab_directory} --recovery=failed", shell=True)

        file_path = os.path.join(crab_directory, "results/failedLumis.json")
        failed_lumis = self.process_failed_lumis_file(file_path)

        with open(os.path.join(crab_directory, "results/failedFiles.json")) as file:
            failed_files_json = json.load(file)
            failed_files = [path for paths in failed_files_json.values() for path in paths]

        return dict(lumiBlocks=failed_lumis, filenames=failed_files)

    @staticmethod
    def notify(topic: str = "ryan_crab", description: str = "Job Finished"):
        requests.post(
            f"https://ntfy.sh/{topic}", data=description.encode(encoding="utf-8")
        )

    @staticmethod
    def submit_cms_job_locally(config_name:str='config.py'):
        subprocess.run(f"cmsRun {config_name}",
                        shell=True)

    @staticmethod
    def submit_crab_job(config_name:str='config.py', template_file:str='config_template.py',
                        yaml_file:str='job_options.yml'):
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='CrabManager',
                                     description="Command-line utility to facilitate the submission of crab jobs"
                                     )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate
    generate_parser = subparsers.add_parser("generate",
                                            help="Generate a config file only")
    generate_parser.add_argument('--year', choices=[2022, 2023], required=True)
    generate_parser.add_argument('--era', choices=['C', 'D', 'E', 'F', 'G'],
                                 required=True)
    generate_parser.add_argument('--requestName', required=True)
    generate_parser.add_argument('--channel', choices['Muon', 'Tau', 'EGamma'],
                                 required=True)
    generate_parser.add_argument('--isRealData', default=True)
    generate_parser.add_argument('--templateDir', default="templates")
    generate_parser.add_argument('--template', required=True)
    generate_parser.add_argument('--config', required=True)
    parser.add_argument('-d', '--crabDirectory')

    # Subcommand: run
    run_parser = subparsers.add_parser("run",
                                            help="Run pre-existing config file")
    run_parser.add_argument("--local", action='store_true')
    run_parser.add_argument('-c', '--configName', default="config.py")

    args = parser.parse_args()

    if args.command == 'generate':
        gen.render_template(args.template, args.config, args.year, args.era,
                            args.dataset, args.templateDir)
        
    if args.command == 'run_local':
        handler = CrabHandler()
        values = handler.grab_failed_lumis_and_files(crab_directory=args.crabDirectory)
        handler.config_generator(args.configName,
                                 parameters = {
                                    "year": args.year,
                                    "era" : args.era,
                                    "isRealData": args.isRealData,
                                    "filenames": values["filenames"],
                                    "lumiBlocks": values["lumiBlocks"]})
        CrabHandler.submit_cms_job(args.configName)


