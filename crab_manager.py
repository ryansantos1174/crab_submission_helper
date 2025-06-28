import subprocess
import sys
from typing import Optional

import pandas as pd

class CrabHandler(): 

    bad_exit_codes: tuple = (50660)
    site_chances: int = 5

    resubmit_jobs: dict[int, dict]= None
    directories: Optional[list[str]] = None
    

    def crab_status(self, crab_directory:str) -> pd.DataFrame:
        # Submit crab status command on given crab directory
        output = subprocess.run(f"crab status -d {crab_directory} --json", shell=True,
                    capture_output=True, text=True).stdout

        start = output.find('{')
        stop = output.find('Log')
        # Remove last log file line and the head of the file
        output = output[start:stop]

        return pd.read_json(output).transpose()

    def get_failed_job_ids(self, submitted_jobs: pd.DataFrame) -> pd.DataFrame:

        failed_ids = submitted_jobs[submitted_jobs["State"] == "failed"][["JobIds", "SiteHistory"]]
        print(failed_ids)
        latest_failed_ids = failed_ids["JobIds"].apply(lambda x: x[-1])
        print(latest_failed_ids)

        self.resubmit_jobs = {key:{} for key in list(latest_failed_ids["JobIds"])}

        return latest_failed_ids
    

    def check_location(self, submitted_jobs: pd.DataFrame):
        sites = submitted_jobs[["SiteHistory", "JobIds"]].value_counts().to_dict()
        for (site, job_id), count in sites.items():
            if count >= self.site_chances:
                if job_id not in self.resubmit_jobs:
                    self.resubmit_jobs[job_id] = {}
                self.resubmit_jobs[job_id]["SiteBlacklist"] = site

    def check_error(self):
        ...
        

if __name__ == "__main__":
    crab_status("crab/crab_EGamma0_FiducialMap_2023C_v1")
