#!/usr/bin/env python3
import os
from CRABClient.UserUtilities import config
config = config()

NLayers= __NLAYERS__
request_name = "__REQUEST_NAME__"
if NLayers: 
    config.General.requestName = request_name + "_NLayers"
else:
    config.General.requestName = request_name 
config.General.workArea = "crab_closure_test"
config.General.transferOutputs = True
config.General.transferLogs = False


config.JobType.pluginName = "Analysis"
config.JobType.psetName = "config_cfg.py"
config.JobType.allowUndistributedCMSSW = True


if not NLayers:
    config.Data.inputDataset = "__DATASET__"
    #config.Data.lumiMask = __LUMIMASK__
    config.Data.inputDBS = "global"
    config.Data.splitting = "Automatic"
    config.Data.unitsPerJob=180
else:
    config.Data.inputDBS = "phys03"
    config.Data.userInputFiles = open("__SKIM_FILE__").readlines()
    config.Data.splitting = "FileBased"
    config.Data.unitsPerJob = 1
    config.Site.whitelist = ['T3_US_FNALLPC','T2_US_Purdue','T2_CH_CERN','T2_BR_SPRACE','T2_US_Caltech','T2_US_Florida','T2_US_MIT','T2_US_Nebraska','T2_US_UCSD','T2_US_Wisconsin']



config.Data.publication = False
config.JobType.maxMemoryMB = 3000
config.JobType.numCores = 1
config.Data.outputDatasetTag = request_name



# Uncomment one of the following pairs


config.Data.outLFNDirBase = "/store/group/lpclonglived/DisappTrks/"
config.Site.storageSite = "T3_US_FNALLPC"

#config.Data.outLFNDirBase = "/store/user/%s/" % (user_name)
#config.Site.storageSite = "T2_US_Purdue"


#config.Data.outLFNDirBase = "/store/group/phys_exotica/disappearingTracks/"
#config.Site.storageSite = "T2_CH_CERN"


# config.Data.outLFNDirBase = "/store/user/borzari/"
# config.Site.storageSite = "T2_BR_SPRACE"
