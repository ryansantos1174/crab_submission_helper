#!/usr/bin/env bash
CMSSW_VERSION="CMSSW_15_0_10"
LOG_FILE="Merge_2024_test.log"

# Edit paths to match your use case (ie. change delossan to your user)
CMSSW_SRC="/uscms_data/d3/delossan/${CMSSW_VERSION}/src"
TEST_DIR="${CMSSW_SRC}/DisappTrks/BackgroundEstimation/test"
CRAB_DIR="${TEST_DIR}/crab"
LOG_PATH="/uscms_data/d3/delossan/${LOG_FILE}"

# Add crab directories here relative to the crab directory
# ie. crab_TauTagPt55_2024C_v1_Muon0
# 
#crab_ZtoTauToEleProbeTrk_2024I_v2_EGamma0
TASKS=(
<<<<<<< Updated upstream
#    crab_ZtoTauToMuProbeTrk_2024C_v1_Muon1
    crab_ZtoTauToEleProbeTrk_2024C_v1_EGamma1
    crab_TriggerAnalysis_2024C_v1_Muon0
    crab_TriggerAnalysis_2024C_v1_Muon1
    crab_TauTagPt55_2024C_v1_Muon0
    crab_TauTagPt55_2024C_v1_Muon1
    crab_ZtoTauToMuProbeTrk_2024D_v1_Muon0
    crab_ZtoTauToEleProbeTrk_2024D_v1_EGamma0
    crab_ZtoTauToEleProbeTrk_2024D_v1_EGamma1
    crab_ZtoTauToMuProbeTrk_2024G_v1_Muon0
    crab_TauTagPt55_2024G_v1_Muon0
    crab_TriggerAnalysis_2024G_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024H_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024H_v1_Muon1
    crab_ZtoTauToEleProbeTrk_2024H_v1_EGamma0
    crab_ZtoTauToEleProbeTrk_2024H_v1_EGamma1
    crab_TauTagPt55_2024H_v1_Muon0
    crab_TauTagPt55_2024H_v1_Muon1
    crab_TriggerAnalysis_2024H_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024I_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024I_v1_Muon1
    crab_ZtoTauToEleProbeTrk_2024I_v1_EGamma0
    crab_ZtoTauToEleProbeTrk_2024I_v1_EGamma1
    crab_TauTagPt55_2024I_v1_Muon0
    crab_TauTagPt55_2024I_v1_Muon1
    crab_TriggerAnalysis_2024I_v1_Muon0
    crab_TriggerAnalysis_2024I_v1_Muon1
    crab_ZtoTauToMuProbeTrk_2024I_v2_Muon1
    crab_ZtoTauToEleProbeTrk_2024I_v2_EGamma0
    crab_ZtoTauToEleProbeTrk_2024I_v2_EGamma1
    crab_TauTagPt55_2024I_v2_Muon0
    crab_TauTagPt55_2024I_v2_Muon1
    crab_TriggerAnalysis_2024I_v2_Muon1
=======
    crab_TauTagPt55_2024C_v1_Muon0
    crab_TauTagPt55_2024C_v1_Muon1
    crab_TauTagPt55_2024G_v1_Muon0
    crab_TauTagPt55_2024H_v1_Muon0
    crab_TauTagPt55_2024H_v1_Muon1
    crab_TauTagPt55_2024I_v1_Muon0
    crab_TauTagPt55_2024I_v1_Muon1
    crab_TauTagPt55_2024I_v2_Muon0
    crab_TauTagPt55_2024I_v2_Muon1
    crab_ZtoTauToMuProbeTrk_2024C_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024C_v1_Muon1
    crab_ZtoTauToMuProbeTrk_2024D_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024G_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024H_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024H_v1_Muon1
    crab_ZtoTauToMuProbeTrk_2024I_v1_Muon0
    crab_ZtoTauToMuProbeTrk_2024I_v1_Muon1
    crab_ZtoTauToMuProbeTrk_2024I_v2_Muon1
    crab_ZtoTauToEleProbeTrk_2024C_v1_EGamma1
    crab_ZtoTauToEleProbeTrk_2024D_v1_EGamma0
    crab_ZtoTauToEleProbeTrk_2024D_v1_EGamma1
    crab_ZtoTauToEleProbeTrk_2024H_v1_EGamma0
    crab_ZtoTauToEleProbeTrk_2024H_v1_EGamma1
    crab_ZtoTauToEleProbeTrk_2024I_v1_EGamma0
    crab_ZtoTauToEleProbeTrk_2024I_v1_EGamma1
    crab_ZtoTauToEleProbeTrk_2024I_v2_EGamma0
    crab_ZtoTauToEleProbeTrk_2024I_v2_EGamma1
>>>>>>> Stashed changes
)

cd "${CMSSW_SRC}"
set +u
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval "$(scramv1 runtime -sh)"
set -u

<<<<<<< Updated upstream
# Merge each task
for task in "${TASKS[@]}"; do
    echo "=== Merging task: ${task} ==="
    crab_helper merge -v --hist --copy -r "${TEST_DIR}" \
        -l "${LOG_PATH}" \
        -d "${CRAB_DIR}" \
        --task "${task}"
=======
for task in "${TASKS[@]}"; do
crab_helper merge -v --group_files --hist --copy -r "${TEST_DIR}" \
    -l "${LOG_PATH}" \
    -d "${CRAB_DIR}" \
    --task "$task"
>>>>>>> Stashed changes
done
