"""
Miscellaneous functions that are used to help write other code (ie. functions
that don't necessarily help with crab commands, parsing, notifications, or google sheet
functionality).
"""
import re
import datetime

from pathlib import Path
from .config import PROJECT_ROOT, DATA_DIR


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

def edit_crab_config_for_recovery(
        crab_config: Path,
        lumimask_path: Path,
        units_per_job: int = 10
) -> Path:
    """
    Edit crab configuration file to make it suitable for a crab recovery task.

    Replace some values within an already generated crab configuration. This
    includes the request_name where we append recovery_v{1,2,...}, the lumimask
    where we use the lumimask created by crab report, and the unitsPerJob

    :param crab_config: Path object pointing to crab configuration file used by
        task that you are creating recovery task for
    :type crab_config: Path
    :param lumimask_path: Path to lumimask file you would like to use in recovery task
    :type lumimask_path: Path
    :param unitsPerJob: Number of units (generally lumisections) you want to process
        in each crab job. This parameter can be optimized to help with memory issues.
    :type unitsPerJob: int
    :return: Path to edited crab configuration file
    :rtype: Path

    :raises FileNotFoundError: Raises if crab_config or lumimask file cannot be resolved
    """
    if not crab_config.exists():
        raise FileNotFoundError(f"Could not resolve crab configuration file: {str(crab_config)} ")
    if not lumimask_path.exists():
        raise FileNotFoundError(f"Could not resolve lumimask file: {str(lumimask_path)}")

    request_name_pattern = re.compile(
        r"^(\s*config\.General\.requestName\s*=\s*)(.*?)(?:\s*\+\s*'(_recovery_v(\d+))')?\s*$",
        re.MULTILINE,
    )

    lumimask_pattern = re.compile(
        r"(\s*config\.Data\.lumiMask\s*=\s*)(.+)"
    )

    units_per_job_pattern = re.compile(
        r"(\s*config\.Data\.unitsPerJob\s*=\s*)(.+)"
    )

    text = crab_config.read_text()

    # Update request_name while incrementing version number
    def _requestname_repl(m: re.Match) -> str:
        lhs = m.group(1)
        base_expr = m.group(2).rstrip()
        version_digits = m.group(4)

        if version_digits is None:
            return f"{lhs}{base_expr} + '_recovery_v1'"
        return f"{lhs}{base_expr} + '_recovery_v{int(version_digits) + 1}'"

    text, n_subs = request_name_pattern.subn(_requestname_repl, text)

    if n_subs == 0:
        raise ValueError(
            "No config.General.requestName assignment found to increment version."
        )

    def _lumimask_repl(m: re.Match) -> str:
        lhs = m.group(1)
        return f"{lhs}'{lumimask_path}'"

    text, n_subs = lumimask_pattern.subn(_lumimask_repl, text)

    if n_subs == 0:
        raise ValueError(
            "No config.Data.lumiMask pattern found!"
        )

    def _units_repl(m: re.Match) -> str:
        lhs = m.group(1)
        return f"{lhs}{units_per_job}"

    text, n_subs = units_per_job_pattern.subn(_units_repl, text)

    if n_subs == 0:
        raise ValueError(
            "No config.Data.unitsPerJob pattern found!"
        )

    timestamp_dir = (
        DATA_DIR
        / "generated"
        / datetime.datetime.now().strftime("%Y%m%d_%H%M")
    )
    timestamp_dir.mkdir(parents=True)

    # Write to timestamp dir and return path to it
    crab_recovery_config_file = timestamp_dir / (crab_config.stem + "_recovery" + crab_config.suffix)
    
    crab_recovery_config_file.write_text(text)

    return crab_recovery_config_file



    

    

    
