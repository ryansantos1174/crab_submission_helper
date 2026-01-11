"""
File to define project accessible constants ie. PROJECT_ROOT_DIRECTORY
"""
from pathlib import Path
from enum import Enum, auto

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "crab_submission_helper" / "data"

class JobStatus(Enum):
    Failed = auto()
    Finished = auto()
    Processing = auto()
    Unknown = auto()
