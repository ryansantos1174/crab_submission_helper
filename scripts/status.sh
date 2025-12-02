#!/usr/bin/env sh

# Setup CMSSW environment
cd /uscms_data/d3/delossan/CMSSW_15_0_10/src
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd -
echo $(hostname) >> /uscms_data/d3/delossan/identify_yourself.log
crab_helper status -v -r /uscms_data/d3/delossan/CMSSW_15_0_10/src/DisappTrks/BackgroundEstimation/test/ \
    -l /uscms_data/d3/delossan/crab_status.log \
    -d /uscms_data/d3/delossan/CMSSW_15_0_10/src/DisappTrks/BackgroundEstimation/test/crab/ \
    --email --ntfy
