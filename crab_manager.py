import subprocess
import sys
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
        print(failed_ids)
        latest_failed_ids = failed_ids["JobIds"].apply(lambda x: x[-1])
        print(latest_failed_ids)

        self.resubmit_jobs = {key: {} for key in list(latest_failed_ids)}

        return latest_failed_ids

    def check_location(self, submitted_jobs: pd.DataFrame):
        sites = submitted_jobs[["SiteHistory", "JobIds"]].value_counts().to_dict()
        for (site, job_id), count in sites.items():
            if count >= self.site_chances:
                if job_id not in self.resubmit_jobs:
                    self.resubmit_jobs[job_id] = {}
                self.resubmit_jobs[job_id]["SiteBlacklist"] = site

    def check_error(self): ...

    def prepare_for_local_submission(self, config_file_path: str, crab_directory: str):
        # Run Crab submit
        subprocess.run(f"crab report -d {crab_directory}", shell=True)

        with open(os.path.join(crab_directory, "failedLumis.json")) as file:
            failed_lumis = json.load(file)
        with open(os.path.join(crab_directory, "failedFiles.json")) as file:
            failed_files = json.load(file)

        ...

    def config_generator(self, filename: str, parameters: dict) -> None:
        config_template = """
        from DisappTrks.BackgroundEstimation.config_cfg import *
        from DisappTrks.StandardAnalysis.customize import *

        if not os.environ["CMSSW_VERSION"].startswith ("CMSSW_12_4_") and not os.environ["CMSSW_VERSION"].startswith ("CMSSW_13_0_"):
            print("Please use a CMSSW_12_4_X or CMSSW_13_0_X release...")
            sys.exit (0)

        process = customize (process, "{year}", "{era}", realData={isRealData}, applyPUReweighting = False, applyISRReweighting = False, applyTriggerReweighting = False, applyMissingHitsCorrections = False, runMETFilters = False)

        process.source.fileNames = cms.untracked.vstring({filenames})
        process.source.lumisToProcess=cms.untracked.VLuminosityBlockRange({lumiBlocks})
        """.format(
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
    ...
