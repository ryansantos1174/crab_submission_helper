import subprocess
import textwrap
import sys
import os
from typing import Optional
import requests
import json

import pandas as pd

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

    def grab_failed_lumis_and_files(self, config_file_path: str, crab_directory: str)-> dict[str, str]:
        # Run Crab submit
        subprocess.run(f"crab report -d {crab_directory}", shell=True)

        with open(os.path.join(crab_directory, "failedLumis.json")) as file:
            failed_lumis = self.process_failed_lumis_file(file)
        with open(os.path.join(crab_directory, "failedFiles.json")) as file:
            failed_files = list(json.load(file).keys())

        return dict(lumiBlocks=failed_lumis, filenames=failed_files)

    def config_generator(self, filename: str, parameters: dict) -> None:
        config_template = textwrap.dedent("""\
        from DisappTrks.BackgroundEstimation.config_cfg import *
        from DisappTrks.StandardAnalysis.customize import *

        if not os.environ["CMSSW_VERSION"].startswith ("CMSSW_12_4_") and not os.environ["CMSSW_VERSION"].startswith ("CMSSW_13_0_"):
            print("Please use a CMSSW_12_4_X or CMSSW_13_0_X release...")
            sys.exit (0)

        process = customize (process, "{year}", "{era}", realData={isRealData}, applyPUReweighting = False, applyISRReweighting = False, applyTriggerReweighting = False, applyMissingHitsCorrections = False, runMETFilters = False)

        process.source.fileNames = cms.untracked.vstring({filenames})
        process.source.lumisToProcess=cms.untracked.VLuminosityBlockRange({lumiBlocks})
        """).format(
            year=parameters["year"],
            era=parameters["era"],
            isRealData=parameters["isRealData"],
            filenames=parameters["filenames"],
            lumiBlocks=parameters["lumiBlocks"],
        )

        with open(filename, "w") as file:
            file.write(config_template)

        # Format code after writing
        subprocess.run(["black", filename], check=True)

    @staticmethod
    def notify(topic: str = "ryan_crab", description: str = "Job Finished"):
        requests.post(
            f"https://ntfy.sh/{topic}", data=description.encode(encoding="utf-8")
        )


if __name__ == "__main__":
    handler = CrabHandler()
    handler.config_generator("test.py",
        parameters = {
            "year": "2022",
            "era": "A",
            "isRealData": True,
            "filenames": '"file1.root", "file2.root"',
            "lumiBlocks": '"123:1-123:100"',
        })
