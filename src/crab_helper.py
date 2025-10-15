#!/usr/bin/env python3
import argparse
import lib.crab_helper as ch
import logging

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
print(log_level)
logging.basicConfig(
    filename=args.log,
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if args.command == 'submit':
    print("Crab submit is currently not implemented")
    ...
if args.command == 'status':
    logging.info("Running crab status")
    crab_directories = ch.grab_crab_directories(crab_directory=args.directory)

    for directory in crab_directories:
        logging.debug("Looping over directories")
        statuses = ch.get_crab_status(directory, run_directory=args.run_dir)
        if statuses["Finished"] and not statuses["Failed"]:
            logging.info(f"Task {str(directory).split('/')[-1]} finished")
        elif statuses["Failed"] and statuses["Finished"]:
            logging.info(f"Task has failed jobs: {str(directory).split('/')[-1]}")
        else:
            logging.info(f"Serious issue with job {str(directory).split('/')[-1]}")

if args.command == 'resubmit':
    logging.info("Running crab resbumit")
    crab_directories = ch.grab_crab_directories(crab_directory=args.directory)
    print(f"Running over following crab directoies {[directory for directory in crab_directories]}")
    logging.debug(f"Running over following crab directoies {crab_directories}")

    for directory in crab_directories:
        # TODO: Implement way to apply resubmission criteria like maxmemory or siteblacklist
        # without affecting all submissions
        return_code, command = ch.crab_resubmit(str(directory), run_directory=args.run_dir)

        logging.debug(f"Ran crab command: {command}")
        logging.debug(f"Crab command returned status: {return_code}")

        if return_code == 192:
            logging.warning(f"No jobs to resubmit for task {str(directory).split('/')[-1]}")
        elif return_code != 0:
            logging.error(f"Crab submit command did not execute correctly: {command}")
            logging.error(f"Crab error code: {return_code}")
