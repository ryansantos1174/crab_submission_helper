#!/usr/bin/env python3
import os
from CRABClient.UserUtilities import config
config = config()

request_name = '__REQUEST_NAME__'
config.General.requestName = request_name
config.General.workArea = 'crab'
config.General.transferOutputs = True
config.General.transferLogs = True


config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'config_cfg.py'
config.JobType.allowUndistributedCMSSW = True


config.Data.inputDataset = "__DATASET__"

if "2022" in request_name:
    config.Data.lumiMask = "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json"
elif "2023" in request_name:
    config.Data.lumiMask = "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json"

config.Data.inputDBS = 'global'
config.Data.unitsPerJob = 20
config.Data.splitting = 'LumiBased'


config.Data.publication = False
config.JobType.maxMemoryMB = 3000
config.JobType.numCores = 1
config.Data.outputDatasetTag = request_name



# Uncomment one of the following pairs


config.Data.outLFNDirBase = '/store/group/lpclonglived/DisappTrks/'
config.Site.storageSite = 'T3_US_FNALLPC'

#config.Data.outLFNDirBase = '/store/user/%s/' % (user_name)
#config.Site.storageSite = 'T2_US_Purdue'


#config.Data.outLFNDirBase = '/store/group/phys_exotica/disappearingTracks/'
#config.Site.storageSite = 'T2_CH_CERN'


# config.Data.outLFNDirBase = '/store/user/borzari/'
# config.Site.storageSite = 'T2_BR_SPRACE'
