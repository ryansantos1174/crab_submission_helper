#!/usr/bin/env bash
set -euo pipefail

CMSSW_VERSION="CMSSW_15_0_10"
BATCH_FILE="2024_FakeTracks_background.yml"
LOG_FILE="FakeTracks_2024EF.log"

CMSSW_SRC="/uscms_data/d3/delossan/${CMSSW_VERSION}/src"
TEST_DIR="${CMSSW_SRC}/DisappTrks/BackgroundEstimation/test"
CRAB_DIR="${TEST_DIR}/crab"
BATCH_PATH="${CMSSW_SRC}/crab_submission_helper/batch_files/${BATCH_FILE}"
LOG_PATH="/uscms_data/d3/delossan/${LOG_FILE}"

cd "${CMSSW_SRC}"
set +u
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "$(scramv1 runtime -sh)"
set -u

crab_helper submit -r "${TEST_DIR}" \
  -l "${LOG_PATH}" \
  -d "${CRAB_DIR}" \
  --batch_file "${BATCH_PATH}" \
