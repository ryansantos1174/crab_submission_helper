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
        action="store_true",
        help="Remove intermediate files after a successful merge+copy.",
    )

    parser.add_argument(
        "--dry-run",
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

    eos = EOSHelper('/store/group/lpclonglived/DisappTrks/')

    for p in paths:
        print(f"Processing: {p}")

        timestamp_subdir = eos.grab_files_and_subdirectories(str(p))

        # Inside of directories there should only be skim files, hist files, and the log directory
        # If I pass it the base directory there will first be the timestamp directory.
        timestamp_subdirectories = eos.filter_files(timestamp_subdir, eos.is_subdir)

        for directory in timestamp_subdirectories:
            entries = eos.grab_files_and_subdirectories(directory)

            files = eos.filter_files(entries, eos.is_file)

            unique_selections_files: dict[str, list[str]] = ph.group_files(files, ph.group_by_selection)

            for selection, grouped_files in unique_selections_files.items():
                hist_files = eos.filter_files(grouped_files, eos.regex_filter(r'^hist.*\.root$'))
                skim_files = eos.filter_files(grouped_files, eos.regex_filter(r'^skim.*\.root$'))

                hist_output_file_name = f"hist_{p.stem}_{selection}_{directory.rsplit('/', maxsplit=1)[-1]}_merged.root"
                skim_output_file_name = f"skim_{p.stem}_{selection}_{directory.rsplit('/', maxsplit=1)[-1]}_merged.root"

                proceed_with_hist_deletion = False
                proceed_with_skim_deletion = False

                if args.dryrun:
                    print("Would merge hist files: ")
                    print(hist_files)

                    print("Would merge skim files: ")
                    print(skim_files)

                    continue

                try: 
                    CrabHelper.merge_files(hist_files, hist_output_file_name, is_skim_file=False)
                    EOSHelper.copy_file(hist_output_file_name, args.output_dir)
                    proceed_with_hist_deletion = True
                except Exception as e:
                    logger.exception("Failed to merge hist files. Will not delete intermediate files!")

                try: 
                    CrabHelper.merge_files(skim_files, skim_output_file_name, is_skim_file=True)
                    EOSHelper.copy_file(skim_output_file_name, args.output_dir)
                    proceed_with_skim_deletion = True

                except Exception as e:
                    logger.exception("Failed to merge skim files. Will not delete intermediate files!")


                if not args.remove_files:
                    continue

                if proceed_with_hist_deletion: 
                    EOSHelper.remove_files(hist_files)
                if proceed_with_skim_deletion:
                    EOSHelper.remove_files(skim_files)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())





