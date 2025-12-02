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
from .lib import google_sheet_helper as gsh
from .lib.parse_helper import replace_template_values, parse_task_name
from .lib.notifications import send_ntfy_notification, send_email
from .lib.config import JobStatus

load_dotenv()

##################################
#  Setup command line interface  #
##################################
def add_common_arguments(parser):
    """Add arguments shared by all subcommands."""
    parser.add_argument(
        "-d", "--directory", required=True,
        help="Path to the CRAB project directory"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose logging messages"
    )
    parser.add_argument(
        "-l", "--log", default="crab_helper.log",
        help="Path to log file"
    )
    parser.add_argument(
        "-r", "--rundir", default=None, dest="run_dir",
        help="Path to directory where commands will be run"
    )
    parser.add_argument(
        "--email", action="store_true",
        help="Send a notification to your email"
    )
    parser.add_argument(
        "--ntfy", action="store_true",
        help="Send a notification to your ntfy server"
    )
    return parser

def add_submit_subparser(subparsers, parent):
    parser = subparsers.add_parser(
        "submit",
        parents=[parent],
        help="Initial submission of CRAB job"
    )
    parser.add_argument("--template", type=str,
                        default=Path(__file__).parent / "data" / "templates",
                        help="Path to template directory")
    parser.add_argument("--template_config_file", type=Path,
                         default= conf.PROJECT_ROOT / "configs" / "templates.yml")
    parser.add_argument("--batch_file", type=str, help="Path to batch submission yaml file")
    parser.add_argument("--test", action="store_true", help="Generate submission files but do not submit them")
    return parser

def add_resubmit_subparser(subparsers, parent):
    parser = subparsers.add_parser(
        "resubmit",
        parents=[parent],
        help="Resubmit CRAB jobs"
    )
    parser.add_argument("--maxmemory", type=int, help="Override max memory for jobs")
    parser.add_argument("--siteblacklist", nargs="+", help="Sites to exclude")
    parser.add_argument("--sitewhitelist", nargs="+", help="Sites to prefer")
    return parser

def add_status_subparser(subparsers, parent):
    parser = subparsers.add_parser(
        "status",
        parents=[parent],
        help="Check status of CRAB jobs"
    )
    return parser

def add_recovery_subparser(subparsers, parent):
    parser = subparsers.add_parser(
        "recover",
        parents=[parent],
        help="Create a recovery task for for the given crab task"
    )
    parser.add_argument("--crab_task", type=str, help="Crab task to generate recovery task for", required=True)

def build_parser():
    """Construct the top-level parser."""
    # shared base
    parent_parser = add_common_arguments(argparse.ArgumentParser(add_help=False))

    # main parser
    parser = argparse.ArgumentParser(description="CRAB job management tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register subcommands
    add_submit_subparser(subparsers, parent_parser)
    add_resubmit_subparser(subparsers, parent_parser)
    add_status_subparser(subparsers, parent_parser)
    add_recovery_subparser(subparsers, parent_parser)

    return parser

def main():
    parser=build_parser()
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

        template_files = parse_template_files(args.template, args.run_dir, args.template_config_file)

        ch.batch_submit_jobs(args.batch_file, template_files, test=args.test, run_directory=args.run_dir)

        if args.email and not args.test:
            subject = "Crab submission finished"
            body = ("Your crab submission has finished submitting!\n"
                    "You can keep track of the jobs using the status command and you can resubmit"
                    "any potentially failed jobs with resubmit")
            send_email(subject, body, os.environ["EMAIL"])
        if args.ntfy and not args.test:
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
            logger.info("Cache directory didn't exist. Created directory at %s", cache_dir.resolve())

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%s")
        summary_file = cache_dir / f"crab_summary_{timestamp}.json"

        finished_job = 0
        processing_job = 0
        failed_job = 0
        unknown_job = 0
        for directory in crab_directories:
            logger.debug("Looping over directories")
            statuses:pd.DataFrame = ch.get_crab_status(directory, run_directory=args.run_dir)

            output_directory:str = ch.get_grab_output_directory(directory, run_directory=args.run_dir)

            if (statuses["State"] == "finished").all():
                logger.info("Task %s finished", str(directory).split('/')[-1])
                status = JobStatus.Finished
                finished_job += 1

            elif (statuses['State'] == 'failed').any() and ((statuses['HasUnrecoverableError']).any() or (statuses["TooManyRetries"]).any()):
                logger.info("Task has unrecoverable failed jobs: %s", str(directory).split('/')[-1])
                status = JobStatus.Failed
                failed_job += 1

            elif (statuses['State'] == 'failed').any():
                logger.info("Task has failed jobs: %s", str(directory).split('/')[-1])
                status = JobStatus.Failed
                failed_job += 1

            elif statuses['State'].isin(["purged", "unknown", "invalid"]).any():
                logger.info("Unknown issue with job %s", str(directory).split('/')[-1])
                status = JobStatus.Unknown
                unknown_job += 1

            else:
                logger.info("Task is still running: %s", str(directory).split('/')[-1])
                status = JobStatus.Processing
            # When we reach the Google API limit error 429 will be raised
            try:
                gsh.update_task_status(os.environ["GOOGLE_SHEET_ID"], os.environ["CREDENTIALS"],
                                       str(directory), status, output_directory, force=True)

            except APIError as e:
                # Wait a minute for the API request limit to reset
                logger.debug("Google sheet API rate limit reached waiting 1 minute to proceed")
                time.sleep(60)
                gsh.update_task_status(os.environ["GOOGLE_SHEET_ID"], os.environ["CREDENTIALS"],
                                       str(directory), status, output_directory, force=True)

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

    if args.command == 'recover':
        # Should only pass a single crab directory don't need to recover every job in crab directory
        # Parse task name to determine selection, year, era, and NLayers
        selection, year, era, version, dataset  = parse_task_name(args.crab_task)

        template_files = {
            "config_cfg_template.py": Path(args.run_dir) / "config_cfg.py",
            "crab_template.py" : Path(args.run_dir) / "crab_cfg.py",
            "config_selections_template.py": Path(args.run_dir) / "../python/config.py"
        }

        replace_template_values(template_files, replacement)
        ch.submit_crab_job()
        args.crab_task

        # Run crab recovery command to generate necessary json files


        # Check whether it is an NLayers or not which will tell you whether you need to check the files
        # or the lumisection to process

        # Template file should be nearly identical so that the files get
        # placed in the same output directory but there needs to be a new
        # requestName so as to not collide with previous task.


    if args.command == 'resubmit':
        logger.info("Running crab resbumit")
        crab_directories = ch.grab_crab_directories(crab_directory=args.directory)
        logger.debug(f"Running over following crab directories {crab_directories}")

        for directory in crab_directories:
            # TODO: Implement way to apply resubmission criteria like maxmemory or siteblacklist
            # without affecting all submissions
            return_code, command = ch.crab_resubmit(str(directory), resubmit_options={"maxmemory": 4000}, run_directory=args.run_dir)

            logger.debug(f"Ran crab command: {command}")
            logger.debug(f"Crab command returned status: {return_code}")

            if return_code == 192:
                logger.warning(f"No jobs to resubmit for task {str(directory).split('/')[-1]}")
            elif return_code != 0:
                logger.error(f"Crab submit command did not execute correctly: {command}")
                logger.error(f"Crab error code: {return_code}")

        if args.email:
            subject = "Crab status"
            body = ("Your crab jobs have been resubmitted")
            send_email(subject, body, os.environ["EMAIL"])
        if args.ntfy:
            body = ("Your crab jobs have been resubmitted")
            send_ntfy_notification(body)
        logger.info("Resubmit command finished")
