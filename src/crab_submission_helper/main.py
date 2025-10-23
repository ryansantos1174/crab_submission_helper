#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from gspread.exceptions import APIError
import pandas as pd

from .lib import crab_helper as ch
from .lib.google_sheet_helper import update_task_status
from .lib.notifications import send_ntfy_notification, send_email

load_dotenv()
##################################
#  Setup command line interface  #
##################################
# Shared arguments go here
def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-d", "--directory",
        required=True,
        help="Path to the CRAB project directory"
    )

    parent_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose logging messages"
    )
    parent_parser.add_argument(
        "-l", "--log",
        default="crab_helper.log",
        help="Path to log file"
    )

    parent_parser.add_argument(
        "-r", "--rundir", default=None, dest="run_dir",
        help="Path to directory where commands will be run"
    )

    parent_parser.add_argument(
        "--email", default=False, action="store_true",
        help="Whether to send a notification to your email"
    )

    parent_parser.add_argument(
        "--ntfy", default=False, action="store_true",
        help="Whether to send a notification to your ntfy server"
    )

    parser = argparse.ArgumentParser(description="CRAB job management tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Each subcommand reuses the parent parser
    parser_submit = subparsers.add_parser(
        "submit",
        parents=[parent_parser],
        help="Initial submission of crab job"
    )
    parser_submit.add_argument("--template", type=str, help="Path to template directory")
    parser_submit.add_argument("--batch_file", type=str, help="Path to batch submission yaml file")

    parser_resubmit = subparsers.add_parser(
        "resubmit",
        parents=[parent_parser],
        help="Resubmit CRAB jobs"
    )
    parser_resubmit.add_argument("--maxmemory", type=int)
    parser_resubmit.add_argument("--siteblacklist", nargs="+")
    parser_resubmit.add_argument("--sitewhitelist", nargs="+")


    parser_status = subparsers.add_parser(
        "status",
        parents=[parent_parser],
        help="Resubmit CRAB jobs"
    )

    args = parser.parse_args()

    ###############
    # Set Logging #
    ###############
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    file_handler = logging.FileHandler(args.log)
    console_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[file_handler, console_handler]
    )
    logger = logging.getLogger(__name__)

    if args.command == 'submit':
        # TODO: Add in check to see if job has already been submitted which would cause crab to not submit job

        # Generate template_files dict needed for batch_submit_jobs
        # Give the mapping for all possible template files here. The crab_template.py
        # and crab_template_nlayers.py will overwrite each other but the logic to avoid this
        # is inside batch_submit_jobs()
        template_files = {"/uscms_data/d3/delossan/CMSSW_13_0_13/src/crab_submission_helper/data/templates/config_cfg_template.py" : f"{args.run_dir}config_cfg.py",
                        "/uscms_data/d3/delossan/CMSSW_13_0_13/src/crab_submission_helper/data/templates/crab_template.py" : f"{args.run_dir}crab_cfg.py",
                        "/uscms_data/d3/delossan/CMSSW_13_0_13/src/crab_submission_helper/data/templates/config_selections_template.py" : f"{args.run_dir}/../python/config.py",
                        "/uscms_data/d3/delossan/CMSSW_13_0_13/src/crab_submission_helper/data/templates/crab_template_nlayers.py": f"{args.run_dir}crab.py"}
        ch.batch_submit_jobs(args.batch_file, template_files, test=False, run_directory=args.run_dir)

        if args.email:
            subject = "Crab submission finished"
            body = ("Your crab submission has finished submitting!\n"
                    "You can keep track of the jobs using the status command and you can resubmit"
                    "any potentially failed jobs with resubmit")
            send_email(subject, body, os.environ["EMAIL"])
        if args.ntfy:
            send_ntfy_notification("Your crab submission has finished submitting!\n"
                    "You can keep track of the jobs using the status command and you can resubmit"
                    "any potentially failed jobs with resubmit")
        logger.info("Submission finished")

    if args.command == 'status':
        logger.info("Running crab status")
        crab_directories = ch.grab_crab_directories(crab_directory=args.directory)

        finished_status: int = 0
        failed_jobs_status: int = 0
        processing_jobs_status: int = 0
        unknown_status: int = 0
        index = 0

        # Setup cache to keep status of jobs
        project_root = Path(__file__).parent.parent
        cache_dir = project_root / ".cache"

        if cache_dir.exists() and cache_dir.is_dir():
            logger.info("Cache directory exists. Using preexisting directory")
        else:
            cache_dir.mkdir()
            logger.info(f"Cache directory didn't exist. Created directory at {cache_dir.resolve()}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%s")
        summary_file = cache_dir / f"crab_summary_{timestamp}.json"

        finished_job = 0
        processing_job = 0
        failed_job = 0
        unknown_job = 0
        for directory in crab_directories:
            logger.debug("Looping over directories")
            statuses:pd.DataFrame = ch.get_crab_status(directory, run_directory=args.run_dir)


            if (statuses["State"] == "finished").all():
                logger.info(f"Task {str(directory).split('/')[-1]} finished")
                status = "Finished"
                finished_job += 1

            elif (statuses['State'] == 'failed').any() and ((statuses['HasUnrecoverableError']).any() or (statuses["TooManyRetries"]).any()):
                logger.info(f"Task has unrecoverable failed jobs: {str(directory).split('/')[-1]}")
                status = "Unrecoverable Error"
                failed_job += 1

            elif (statuses['State'] == 'failed').any():
                logger.info(f"Task has failed jobs: {str(directory).split('/')[-1]}")
                status = "Failed Jobs"
                failed_job += 1

            elif statuses['State'].isin(["purged", "unknown", "invalid"]).any():
                logger.info(f"Unknown issue with job {str(directory).split('/')[-1]}")
                status = "Unknown Issue"
                unknown_job += 1

            else:
                logger.info(f"Task is still running: {str(directory).split('/')[-1]}")
                status = "Processing"

            # When we reach the Google API limit error 429 will be raised
            try:
                update_task_status(os.environ["GOOGLE_SHEET_ID"], os.environ["CREDENTIALS"],
                                    str(directory), status, force=True)
            except APIError as e:
                # Wait a minute for the API request limit to reset
                logger.debug("Google sheet API rate limit reached waiting 1 minute to proceed")
                time.sleep(60)
                update_task_status(os.environ["GOOGLE_SHEET_ID"], os.environ["CREDENTIALS"],
                                    str(directory), status, force=True)

            try:
                unrecoverable_job_ids = statuses.loc[statuses["HasUnrecoverableError"], "job_id"].tolist()
            except KeyError:
                unrecoverable_job_ids = []

        if args.email:
            subject = "Crab status"
            body = ("The status of your crab jobs has been recieved."
                    f"There are {finished_job} finished tasks, {processing_jobs_status} tasks are still running, {failed_jobs_status} tasks with failed jobs, and {unknown_status} tasks with an unknown status."
                    "Please resubmit jobs with the submit command to fix the failed jobs. If the number of failed jobs seems to remain consistent over several resubmits please manually check."
                    "For the jobs with an unknown status, you will probably need to check these jobs manually.")
            send_email(subject, body, os.environ["EMAIL"])
        if args.ntfy:
            body = ("The status of your crab jobs has been recieved."
                    f"There are {finished_job} finished tasks, {processing_jobs_status} tasks are still running, {failed_jobs_status} tasks with failed jobs, and {unknown_status} tasks with an unknown status."
                    "Please resubmit jobs with the submit command to fix the failed jobs. If the number of failed jobs seems to remain consistent over several resubmits please manually check."
                    "For the jobs with an unknown status, you will probably need to check these jobs manually.")
            send_ntfy_notification(body)
        logger.info("Status command finished")


    if args.command == 'resubmit':
        logger.info("Running crab resbumit")
        crab_directories = ch.grab_crab_directories(crab_directory=args.directory)
        logger.debug(f"Running over following crab directories {crab_directories}")

        for directory in crab_directories:
            # TODO: Implement way to apply resubmission criteria like maxmemory or siteblacklist
            # without affecting all submissions
            return_code, command = ch.crab_resubmit(str(directory), run_directory=args.run_dir)

            logger.debug(f"Ran crab command: {command}")
            logger.debug(f"Crab command returned status: {return_code}")

            if return_code == 192:
                logger.warning(f"No jobs to resubmit for task {str(directory).split('/')[-1]}")
            elif return_code != 0:
                logger.error(f"Crab submit command did not execute correctly: {command}")
                logger.error(f"Crab error code: {return_code}")

        if args.email:
            subject = "Crab status"
            body = ("The status of your crab jobs has been recieved."
                    f"There are {good_status} finished tasks, {bad_status} tasks with failed jobs, and {unknown_status} tasks with an unknown status."
                    "Please resubmit jobs with the submit command to fix the failed jobs. If the number of failed jobs seems to remain consistent over several resubmits please manually check."
                    "For the jobs with an unknown status, you will probably need to check these jobs manually.")
            send_email(subject, body, os.environ["EMAIL"])
        if args.ntfy:
            body = ("The status of your crab jobs has been recieved."
                    f"There are {good_status} finished tasks, {bad_status} tasks with failed jobs, and {unknown_status} tasks with an unknown status."
                    "Please resubmit jobs with the submit command to fix the failed jobs. If the number of failed jobs seems to remain consistent over several resubmits please manually check."
                    "For the jobs with an unknown status, you will probably need to check these jobs manually.")
            send_ntfy_notification(body)
        logger.info("Resubmit command finished")
