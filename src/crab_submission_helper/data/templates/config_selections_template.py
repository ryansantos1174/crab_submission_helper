from DisappTrks.StandardAnalysis.protoConfig_cfg import *


def getNLayersChannelVariations (chName):
    return [globals()[chName + x] for x in ['NLayers4', 'NLayers5', 'NLayers6plus']]

selection = "__SELECTION__"
NLayers = False

if not NLayers:
    if selection == "TauTagPt55":
        add_channels  (process,  [TauTagPt55],         histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers + tauMETTriggerProducer,ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [TauTagPt55MetTrig],  histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
    if selection == "ZtoTauToMuProbeTrk":
        add_channels  (process,  [ZtoTauToMuProbeTrk],                       histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + tauToMuonTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [ZtoTauToMuProbeTrkWithFilter],             histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + tauToMuonTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [ZtoTauToMuProbeTrkWithSSFilter],           histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + tauToMuonTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
    elif selection == "ZtoTauToEleProbeTrk":
        add_channels  (process,  [ZtoTauToEleProbeTrk],             histSetsElectron, weightsWithEleSF, scaleFactorProducersWithElectrons, collMap, variableProducers + tauToElectronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [ZtoTauToEleProbeTrkWithFilter],   histSetsElectron, weightsWithEleSF, scaleFactorProducersWithElectrons, collMap, variableProducers + tauToElectronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [ZtoTauToEleProbeTrkWithSSFilter], histSetsElectron, weightsWithEleSF, scaleFactorProducersWithElectrons, collMap, variableProducers + tauToElectronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
    elif selection == "ElectronTagPt55":
        add_channels  (process,  [ElectronTagPt55],         histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronMETTriggerProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [ElectronTagPt55MetTrig],  histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
    elif selection == "MuonFiducial":
        add_channels  (process,  [MuonFiducialCalcBeforeOldCuts],  histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [MuonFiducialCalcAfterOldCuts],   histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
    elif selection == "ElectronFiducial":
        add_channels  (process,  [ElectronFiducialCalcBeforeOldCuts], histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True)
        add_channels  (process,  [ElectronFiducialCalcAfterOldCuts],  histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
    elif selection == "TriggerAnalysis":
        add_channels  (process,  [TauTagSkimSingleMuonTriggerSelection],         histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers + tauMETTriggerProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [TauTagSkimMuonTauTriggerSelection],  histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

elif NLayers:
    if selection == "TauTagPt55":
        add_channels  (process,  getNLayersChannelVariations("TauTagPt55"),         histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers + tauMETTriggerProducer, ignoreSkimmedCollections=True)
        add_channels  (process,  getNLayersChannelVariations("TauTagPt55MetTrig"),  histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers, ignoreSkimmedCollections=True)
    if selection == "ZtoTauToMuProbeTrk":
        add_channels  (process,  getNLayersChannelVariations("ZtoTauToMuProbeTrk"),                       histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + tauToMuonTPProducer, ignoreSkimmedCollections=True)
        add_channels  (process,  getNLayersChannelVariations("ZtoTauToMuProbeTrkWithFilter"),             histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + tauToMuonTPProducer, ignoreSkimmedCollections=True)
        add_channels  (process,  getNLayersChannelVariations("ZtoTauToMuProbeTrkWithSSFilter"),           histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + tauToMuonTPProducer, ignoreSkimmedCollections=True)
    elif selection == "ZtoTauToEleProbeTrk":
        add_channels  (process,  getNLayersChannelVariations("ZtoTauToEleProbeTrk"),             histSetsElectron, weightsWithEleSF, scaleFactorProducersWithElectrons, collMap, variableProducers + tauToElectronTPProducer, ignoreSkimmedCollections = False)
        add_channels  (process,  getNLayersChannelVariations("ZtoTauToEleProbeTrkWithFilter"),   histSetsElectron, weightsWithEleSF, scaleFactorProducersWithElectrons, collMap, variableProducers + tauToElectronTPProducer, ignoreSkimmedCollections = False)
        add_channels  (process,  getNLayersChannelVariations("ZtoTauToEleProbeTrkWithSSFilter"), histSetsElectron, weightsWithEleSF, scaleFactorProducersWithElectrons, collMap, variableProducers + tauToElectronTPProducer, ignoreSkimmedCollections = False)
    elif selection == "ElectronTagPt55":
        add_channels  (process,  getNLayersChannelVariations("ElectronTagPt55"),         histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronMETTriggerProducer, ignoreSkimmedCollections = True)
        add_channels  (process,  getNLayersChannelVariations("ElectronTagPt55MetTrig"),  histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True)

if hasattr(process, 'EventJetVarProducer'):
    process.EventJetVarProducer.triggerNames = triggerNamesInclusive
else:
    print()
    print('You haven\'t added any channels. There\'s nothing to do!')
    print()
    sys.exit(0)
