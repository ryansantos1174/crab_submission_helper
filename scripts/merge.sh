#!/usr/bin/env bash
CMSSW_VERSION="CMSSW_15_0_10"
LOG_FILE="Merge_2024.log"

# Edit paths to match your use case (ie. change delossan to your user)
CMSSW_SRC="/uscms_data/d3/delossan/${CMSSW_VERSION}/src"
TEST_DIR="${CMSSW_SRC}/DisappTrks/BackgroundEstimation/test"
CRAB_DIR="${TEST_DIR}/crab"
LOG_PATH="/uscms_data/d3/delossan/${LOG_FILE}"

# Add crab directories here relative to the crab directory
# ie. crab_TauTagPt55_2024C_v1_Muon0
TASKS=(

)

cd "${CMSSW_SRC}"
set +u
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "$(scramv1 runtime -sh)"
set -u


crab_helper merge -v --hist --copy --cleanup -r "${TEST_DIR}" \
    -l "${LOG_PATH}" \
    -d "${CRAB_DIR}" \
    --task
