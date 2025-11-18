from DisappTrks.BackgroundEstimation.config import *
from DisappTrks.StandardAnalysis.customize import *


process = customize (process, '__YEAR__', __ERA__, realData=True, applyPUReweighting = False, applyISRReweighting = False, applyTriggerReweighting = False, applyMissingHitsCorrections = False, runMETFilters = False)
