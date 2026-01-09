"""
Miscellaneous functions that are used to help write other code (ie. functions
that don't necessarily help with crab commands, parsing, notifications, or google sheet
functionality).
"""

from pathlib import Path
from .config import PROJECT_ROOT


def grab_configuration_file(
    task_directory: Path,
    generated_template_directory: Path = (
        Path(PROJECT_ROOT) / "src" / "crab_submission_helper" / "data" / "generated"
    ),
    expected_config_files: int = 3,
) -> list[Path]:
    """
    For a given task, grab the configuration files that were used
    to submit the task.

    task_directory: Resolvable path to the crab task directory (ie. crab/task_directory)
    generated_template_directory
    generated_template_directory: Path to directory storing generated template files (ie. template files with templated values replaced)
    expected_config_files: Number of expected config files that you expect to be found
    """
    # Grab name of task and remove crab prefix
    task_name = task_directory.name.split("_")[1]

    # Look for this task name in the latest timestamped directory in data_directory
    # if it doesn't exist go to the next latest etc.
    sub_dirs = [x for x in generated_template_directory.iterdir() if x.is_dir()]

    while len(sub_dirs) != 0:
        latest_sub_dir: Path = max(sub_dirs)
        matched_config_files: Path = list(latest_sub_dir.glob(f"*{task_name}*"))

        if not matched_config_files:
            sub_dirs.remove(latest_sub_dir)
            continue

        if len(matched_config_files) != expected_config_files:
            raise ValueError(
                f"Found the wrong number of configuration files. Expected {expected_config_files}, got {len(matched_config_files)}"
            )
        break

    if not matched_config_files:
        raise FileNotFoundError(
            f"Could not find config files matching task {task_name} inside {generated_template_directory}"
        )

    return matched_config_files
