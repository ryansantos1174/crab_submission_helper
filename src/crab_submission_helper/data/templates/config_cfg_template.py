from DisappTrks.BackgroundEstimation.config import *
from DisappTrks.StandardAnalysis.customize import *

if not os.environ["CMSSW_VERSION"].startswith ("CMSSW_12_4_") and not os.environ["CMSSW_VERSION"].startswith ("CMSSW_13_0_"):
    print("Please use a CMSSW_12_4_X or CMSSW_13_0_X release...")
    sys.exit (0)

process = customize (process, "__YEAR__", "__ERA__", realData=True, applyPUReweighting = False, applyISRReweighting = False, applyTriggerReweighting = False, applyMissingHitsCorrections = False, runMETFilters = False)


#process.source.fileNames = cms.untracked.vstring(["file:Tau_2022D_Merged.root"])

