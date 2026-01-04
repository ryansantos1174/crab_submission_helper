#!/usr/bin/env sh

CMSSW_VERSION="CMSSW_15_0_10"
LOG_FILE="TauBackground_2024_resubmission.log"

CMSSW_SRC="/uscms_data/d3/delossan/${CMSSW_VERSION}/src"
TEST_DIR="${CMSSW_SRC}/DisappTrks/BackgroundEstimation/test"
CRAB_DIR="${TEST_DIR}/crab"
LOG_PATH="/uscms_data/d3/delossan/${LOG_FILE}"

cd "${CMSSW_SRC}"
set +u
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "$(scramv1 runtime -sh)"
set -u

crab_helper resubmit -v -r "${TEST_DIR}" \
  -l "${LOG_PATH}" \
  -d "${CRAB_DIR}" \
  --email --ntfy
