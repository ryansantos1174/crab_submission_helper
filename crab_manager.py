#!/usr/bin/env python3 
import argparse
import logging
import os
import re
import subprocess

from tqdm import tqdm

import notification


class CrabHandler():
    def __init__(self, log_dir:str, directory:str):
        self.temp_log_directory= log_dir
        self.crab_directory = directory

    def get_status(self):
        resubmission_info = []

        for subdir in tqdm(os.listdir(self.crab_directory)):
            logging.info(f"Running over {subdir}")
            full_path = os.path.join(self.crab_directory, subdir)
            result = subprocess.run(
                ["crab", "status", "--summary", "-d", full_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result.stdout

            # Parse job states
            job_state_matches = re.findall(r"(\w+)\s+[\d\.]+%\s+\(\s*(\d+)/\d+\)", output)
            job_states = {state: int(count) for state, count in job_state_matches}

            # Skip active jobs
            non_terminal_states = {"idle", "running", "transferring", "unsubmitted"}
            if any(job_states.get(state, 0) > 0 for state in non_terminal_states):
                print(f"Skipping {subdir}: jobs still active.")
                continue

            num_failed = job_states.get("failed", 0)
            if num_failed > 0:
                # Find all exit codes
                code_matches = re.findall(r"(\d+)\s+jobs failed with exit code (\d+)", output)
                # Build a string like: "50660:3;8021:7"
                exit_code_summary = ";".join(f"{code}:{count}" for count, code in code_matches)
                print(f"{subdir}: {num_failed} failed jobs with exit codes: {exit_code_summary}")
                resubmission_info.append((subdir, num_failed, exit_code_summary))

        # Save results
        with open("resubmit_candidates.txt", "w") as f:
            for subdir, num_failed, exit_code_summary in resubmission_info:
                f.write(f"{subdir},{num_failed},{exit_code_summary}\n")

    def load_env_file(self, filepath):
        # Get directory of the current script file
        script_dir = os.path.dirname(os.path.realpath(__file__))
        env_path = os.path.join(script_dir, filepath)

        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="CRAB job status and resubmission handler.")
    parser.add_argument(
        "--log_dir", type=str, required=True, help="Path to the log directory"
    )
    parser.add_argument(
        "--crab_dir", type=str, required=True, help="Path to the CRAB job directory"
    )
    parser.add_argument(
        "--env_file", type=str, default=".env", help="Path to the .env file (default: .env)"
    )
    parser.add_argument(
        "--log_level", type=str, default="WARNING", help="Logging level of script (WARNING, ERROR, INFO, DEBUG)")

    parser.add_argument('function', default="status", help="Which command to run. Either status, resubmit, or submit")

    args = parser.parse_args()
    handler = CrabHandler(args.log_dir, args.crab_dir)
    # Get CRAB job status

    # Setting up logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    logging.basicConfig(level=numeric_level)

    if args.function == "status":
        handler.get_status()
    elif args.function == "resubmit":
        logging.error("Resubmit has not been implemented yet")
    elif args.function == "submit":
        logging.error("Submit has not been implemented yet")
        
        
    handler.get_status()
