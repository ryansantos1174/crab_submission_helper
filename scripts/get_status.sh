#!/usr/bin/env sh

# Setup CMSSW environment
cd /uscms_data/d3/delossan/CMSSW_13_0_13/src
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd -

crab_helper status -v -r /uscms_data/d3/delossan/CMSSW_13_0_13/src/DisappTrks/BackgroundEstimation/test/ \
    -l /uscms_data/d3/delossan/crab_status.log \
    -d /uscms_data/d3/delossan/CMSSW_13_0_13/src/DisappTrks/BackgroundEstimation/test/crab/ \
    --email --ntfy
