#!/usr/bin/env python3
import sys
from pathlib import Path
import logging
import argparse

from crab_submission_helper.lib.crab_helper import CrabHelper
import crab_submission_helper.lib.parse_helper as ph
import crab_submission_helper.lib.generators as gen
from crab_submission_helper.lib.eos_helper import EOSHelper
from crab_submission_helper.lib.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

def iter_input_paths(cli_paths: list[str]) -> list[Path]:
    paths: list[Path] = [Path(p) for p in cli_paths]

    # If stdin is piped, read additional paths (one per line)
    if not sys.stdin.isatty():
        for line in sys.stdin:
            s = line.strip()
            if s:
                paths.append(Path(s))

    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process many directory paths passed as args and/or stdin."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Directory paths (also accepts paths from stdin).",
    )

    parser.add_argument(
            "-o", "--output-dir",
            default="/store/user/delossan/2024/",
            help="EOS output directory for merged files.",
        )

    parser.add_argument(
        "--remove-files",
        dest="remove_files",
        action="store_true",
        help="Remove intermediate files after a successful merge+copy.",
    )

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Print what would be merged, but do not merge/copy/remove.",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    paths = iter_input_paths(args.paths)
    if not paths:
        parser.print_usage(sys.stderr)
        return 2

    eos = EOSHelper()

    for p in paths:
        print(f"Processing: {p}")

        # Need to ignore first value from find as that is just the current directory
        timestamp_subdir = eos.grab_files_and_subdirectories(str(p))[1:]

        # Inside of directories there should only be skim files, hist files, and the log directory
        # If I pass it the base directory there will first be the timestamp directory.
        timestamp_subdirectories = eos.filter_files(timestamp_subdir, eos.is_subdir)

        for timestamp_dir in timestamp_subdirectories:
            print(f"Processing {timestamp_dir}")
            numbered_dirs = eos.grab_files_and_subdirectories(timestamp_dir)[1:]
            numbered_dirs = eos.filter_files(numbered_dirs, eos.is_subdir)

            files_to_merge = []
            for num_directory in numbered_dirs: 
                entries = eos.grab_files_and_subdirectories(num_directory, xurl=True)
                #print("entries", entries)

                files_to_merge += eos.filter_files(entries, eos.is_file)
                #print("Files to merge: ", files_to_merge)

            skim_files_to_merge = eos.filter_files(files_to_merge, eos.regex_filter(r'.*skim.*\.root$'))
            hist_files_to_merge = eos.filter_files(files_to_merge, eos.regex_filter(r'.*hist.*\.root$'))


            print("hist_files: ")
            print(hist_files_to_merge[:5])
            print(len(hist_files_to_merge))

            print("skim_files: ")
            print(skim_files_to_merge[:5])
            print(len(skim_files_to_merge))

            try: 
                unique_skim_selections_files: dict[str, list[str]] = ph.group_files(skim_files_to_merge, ph.group_by_selection)
                logger.info("Grouped Files!")
            except AssertionError:
                logger.warning(f"Couldn't group files for {timestamp_dir}")
                continue

            for selection, skim_files in unique_skim_selections_files.items():
                logger.info(
                    "skim_files:\n"
                    "  count: %d\n"
                    "  preview (first 5):\n"
                    "    %s",
                    len(skim_files),
                    "\n    ".join(skim_files[:5]),
                )

                skim_output_file_name = f"skim_{p.stem}_{selection}_{timestamp_dir.rsplit('/', maxsplit=1)[-1]}_merged.root"

                proceed_with_skim_deletion = False

                if args.dry_run:
                    logger.info(
                        "DRY-RUN: would merge skim files:\n"
                        "  total files: %d\n"
                        "  preview (first %d):\n"
                        "    %s",
                        len(skim_files),
                        min(10, len(skim_files)),
                        "\n    ".join(skim_files[:10]),
                    )

                    continue

                try:
                    logger.info("Starting merge of skim files")
                    CrabHelper.merge_files(skim_files, skim_output_file_name, is_skim_file=True)
                    logger.info("Merging Finished")
                    EOSHelper.copy_file(skim_output_file_name, args.output_dir)
                    logger.info("Merged skim file copied to %s", args.output_dir)
                    proceed_with_skim_deletion = True

                except Exception as e:
                    logger.exception("Failed to merge skim files. Will not delete intermediate files!")


                if not args.remove_files:
                    continue

                if proceed_with_skim_deletion:
                    logger.info("About to delete skim files")
                    EOSHelper.remove_files(skim_files)
                    logger.info("Finished deleting files")


            # Hist files don't need to be grouped together by collection 
            if args.dry_run:
                print("Would merge hist files: ")
                print(hist_files_to_merge[:10])
                continue

            proceed_with_hist_deletion = False
            hist_output_file_name = f"hist_{p.stem}_{timestamp_dir.rsplit('/', maxsplit=1)[-1]}_merged.root"
            try:
                logger.info("Starting merge of hist files")
                CrabHelper.merge_files(hist_files_to_merge, hist_output_file_name, is_skim_file=False)
                logger.info("Finished merging")
                EOSHelper.copy_file(hist_output_file_name, args.output_dir)
                logger.info("Copied merged file to %s", args.output_dir)
                proceed_with_hist_deletion = True
            except Exception as e:
                logger.exception("Failed to merge hist files. Will not delete intermediate files!")

            if not args.remove_files:
                continue

            if proceed_with_hist_deletion:
                logger.info("About to remove hist files")
                EOSHelper.remove_files(hist_files_to_merge)
                logger.info("Finished removing files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())





