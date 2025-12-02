"""
File to define project accessible constants ie. PROJECT_ROOT_DIRECTORY
"""
from pathlib import Path
from enum import Enum, auto

PROJECT_ROOT = Path(__file__).resolve().parent

class JobStatus(Enum):
    Finished = auto()
    Processing = auto()
    Failed = auto()
    Unknown = auto()
