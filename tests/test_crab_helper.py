import pytest
from pathlib import Path
<<<<<<< HEAD

from crab_submission_helper.lib.crab_helper import (
    grab_lumi_mask
)
=======
import tempfile
import yaml

from crab_submission_helper.lib.crab_helper import (
    CrabHelper
)
<<<<<<< variant A
import crab_submission_helper.lib.generators as gen
<<<<<<< HEAD
>>>>>>> decf85c (Fix NLayers submission (#2))
=======
>>>>>>> variant B
======= end
>>>>>>> afcc5ea (Start tests for crab_helper.py)

@pytest.fixture
def crab_directory(tmp_path):
    run_directory = tmp_path
    crab_directory = run_directory / "crab"
<<<<<<< HEAD
    task_results_directory = crab_directory / "crab_TauTagPt55_2024C_v1_Muon0" /"results"
    task_results_directory.mkdir(parents=True)
=======
    task_results_directory = crab_directory / "crab_MySelection_2024C_v1_Muon0" / "results"
    task_results_directory.mkdir(parents=True)
<<<<<<< HEAD
    (crab_directory / "crab_TauTagPt55_2024C_v1_Muon0").mkdir()
>>>>>>> decf85c (Fix NLayers submission (#2))
=======
>>>>>>> afcc5ea (Start tests for crab_helper.py)


    return {"run_directory": run_directory,
            "crab_directory": crab_directory,
            "task_results_directory": task_results_directory}

<<<<<<< HEAD


def test_grab_lumi_mask(crab_directory):
    run_dir = crab_directory['run_directory']
    crab_dir = crab_directory['crab_directory']
=======
@pytest.fixture
def setup_CrabHelper(crab_directory):
    return CrabHelper(run_directory=crab_directory['run_directory'], crab_directory=crab_directory['crab_directory'])

@pytest.fixture
def output_directory(tmp_path):
    log_directory = tmp_path / "260103_064010" / "0000" / "log"
    log_directory.mkdir(parents=True)

    TEST_ROOT_FILES = [
        "skim_MySelection_2026_01_03_23h00m28s_994.root",
        "hist_MySelection_2026_01_03_23h00m28s_994.root",

        "skim_MySelection_2026_02_14_09h17m42s_381.root",
        "hist_MySelection_2026_02_14_09h17m42s_381.root",

        "skim_MySelection_2025_12_07_18h55m03s_742.root",
        "hist_MySelection_2025_12_07_18h55m03s_742.root",

        "skim_MySelection_2026_03_21_06h08m59s_615.root",
        "hist_MySelection_2026_03_21_06h08m59s_615.root",

        "skim_MySelection_2025_11_30_14h39m11s_207.root",
        "hist_MySelection_2025_11_30_14h39m11s_207.root",
    ]

    # These should match the job ids above (I know it's jank for now)
    JOB_INDEXES = ['994', '381', '742', '615', '207']

    for file in TEST_ROOT_FILES:
        (log_directory.parent / file).touch(exist_ok=True)

    for job_id in JOB_INDEXES:
        (log_directory / f"cmsRun_{job_id}.log.tar.gz").touch(exist_ok=True)

    return log_directory.parent


def test_grab_lumi_mask(setup_CrabHelper, crab_directory):
    ch = setup_CrabHelper

>>>>>>> decf85c (Fix NLayers submission (#2))
    task_results_dir = crab_directory['task_results_directory']

    lumi_file_expected = task_results_dir / "notFinishedLumis.json"
    lumi_file_expected.touch()

<<<<<<< HEAD

    lumi_file = grab_lumi_mask(task_results_dir.parent, run_dir)
    assert lumi_file == lumi_file_expected

def test_grab_lumi_mask_file_missing(crab_directory):
    run_dir = crab_directory['run_directory']
    crab_dir = crab_directory['crab_directory']
    task_results_dir = crab_directory['task_results_directory']

    with pytest.raises(FileNotFoundError):
        lumi_file = grab_lumi_mask(task_results_dir.parent, run_dir)

    
=======
    lumi_file = ch.grab_lumi_mask(task_results_dir.parent)
    assert lumi_file == lumi_file_expected

def test_grab_lumi_mask_file_missing(setup_CrabHelper, crab_directory):
    ch = setup_CrabHelper
    task_results_dir = crab_directory['task_results_directory']

    with pytest.raises(FileNotFoundError):
        ch.grab_lumi_mask(task_results_dir.parent)

def test_submit_NLayers_job(setup_CrabHelper, crab_directory, output_directory, tmp_path):
    ch = setup_CrabHelper

    batch_file = Path("batch.yml")

    entries = [
        {"YEAR": 2024, "ERA": "C", "ERA_VERSION": 1, "DATASET_VERSION": 0, "SELECTION": "MySelection", "NLAYERS": True},
    ]

    batch_file.write_text(yaml.safe_dump(entries, sort_keys=False))

    template_files_dir = (Path(__file__).parent / "src" / "crab_submission_helper"
                      / "data" / "templates")

    template_files = {}
    output_directory = tmp_path
    for template_file in list(template_files_dir.glob('*')):
        template_files[str(template_file.absolute())] = str(output_directory / template_file.name)

    generating_functions = [add_dataset_type, gen.add_request_name, ch.add_skim_files,]
    #
    ch.batch_submit_jobs(batch_file = str(batch_file),
                         template_files = template_files,
                         generating_functions = generating_functions,
                         test=True)

def add_dataset_type(input_values):
    """
    Needed to fake the dataset type for testing
    """
    return {"DATASET_TYPE": "Muon"}
>>>>>>> decf85c (Fix NLayers submission (#2))
