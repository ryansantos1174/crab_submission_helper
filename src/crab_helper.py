#!/usr/bin/env python3
import argparse
import logging
import os
import time

from dotenv import load_dotenv
from gspread.exceptions import APIError

from lib import crab_helper as ch
from lib.google_sheet_helper import update_task_status

load_dotenv()
##################################
#  Setup command line interface  #
##################################
# Shared arguments go here
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
logging.basicConfig(
    filename=args.log,
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

if args.command == 'submit':
    # TODO: Add in check to see if job has already been submitted which would cause crab to not submit job

    # Generate template_files dict needed for batch_submit_jobs
    # Give the mapping for all possible template files here. The crab_template.py
    # and crab_template_nlayers.py will overwrite each other but the logic to avoid this
    # is inside batch_submit_jobs()
    template_files = {"data/templates/config_cfg_template.py" : f"{args.rundir}config_cfg.py",
                      "data/templates/crab_template.py" : f"{args.rundir}crab_cfg.py",
                      "data/templates/config_selections_template.py" : f"{args.rundir}/../python/config.py",
                      "data/templates/crab_template_nlayers.py": f"{args.rundir}crab.py"}
    ch.batch_submit_jobs(args.batch_file, template_files)



if args.command == 'status':
    logger.info("Running crab status")
    crab_directories = ch.grab_crab_directories(crab_directory=args.directory)

    for directory in crab_directories:
        logger.debug("Looping over directories")
        statuses = ch.get_crab_status(directory, run_directory=args.run_dir)

        if statuses["Finished"] and not statuses["Failed"]:
            logger.info(f"Task {str(directory).split('/')[-1]} finished")
            status = "Finished"
        elif statuses["Failed"] and statuses["Finished"]:
            logger.info(f"Task has failed jobs: {str(directory).split('/')[-1]}")
            status = "Failed Jobs"
        else:
            logger.info(f"Serious issue with job {str(directory).split('/')[-1]}")
            status = "Serious Failure"

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


if args.command == 'resubmit':
    logger.info("Running crab resbumit")
    crab_directories = ch.grab_crab_directories(crab_directory=args.directory)
    logger.debug(f"Running over following crab directoies {crab_directories}")

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
