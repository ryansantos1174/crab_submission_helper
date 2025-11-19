#!/usr/bin/env sh

# Setup CMSSW environment
cd /uscms_data/d3/delossan/CMSSW_15_0_10/src
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd -


crab_helper submit -r /uscms_data/d3/delossan/CMSSW_15_0_10/src/DisappTrks/BackgroundEstimation/test/ \
    -l /uscms_data/d3/delossan/crab_submit_muon_fiducial_maps_2025-11-19.log \
    -d /uscms_data/d3/delossan/CMSSW_15_0_10/src/DisappTrks/BackgroundEstimation/test/crab/ \
    --batch_file /uscms_data/d3/delossan/CMSSW_15_0_10/src/crab_submission_helper/batch_files/2024_fiducial_maps_batch_submission.yaml \
    --test
