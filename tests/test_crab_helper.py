import pytest
from pathlib import Path

from crab_submission_helper.lib.crab_helper import (
    grab_lumi_mask
)

@pytest.fixture
def crab_directory(tmp_path):
    run_directory = tmp_path
    crab_directory = run_directory / "crab"
    task_results_directory = crab_directory / "crab_TauTagPt55_2024C_v1_Muon0" /"results"
    task_results_directory.mkdir(parents=True)


    return {"run_directory": run_directory,
            "crab_directory": crab_directory,
            "task_results_directory": task_results_directory}



def test_grab_lumi_mask(crab_directory):
    run_dir = crab_directory['run_directory']
    crab_dir = crab_directory['crab_directory']
    task_results_dir = crab_directory['task_results_directory']

    lumi_file_expected = task_results_dir / "notFinishedLumis.json"
    lumi_file_expected.touch()


    lumi_file = grab_lumi_mask(task_results_dir.parent, run_dir)
    assert lumi_file == lumi_file_expected

def test_grab_lumi_mask_file_missing(crab_directory):
    run_dir = crab_directory['run_directory']
    crab_dir = crab_directory['crab_directory']
    task_results_dir = crab_directory['task_results_directory']

    with pytest.raises(FileNotFoundError):
        lumi_file = grab_lumi_mask(task_results_dir.parent, run_dir)

    
