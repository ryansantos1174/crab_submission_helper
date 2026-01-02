from DisappTrks.StandardAnalysis.protoConfig_cfg import *


def getNLayersChannelVariations (chName):
    return [globals()[chName + x] for x in ['NLayers4', 'NLayers5', 'NLayers6plus']]

selection = __SELECTION__
NLayers = __NLAYERS__

if not NLayers:
    # Fake Track Selections
    if selection == "BasicSelection":
        add_channels  (process,  [basicSelection],                histSets,  weights,  [],  collMap,  variableProducers,  True)
        add_channels  (process,  [basicSelectionInvertJetMetPhiCut], histSets,  weights,  [],  collMap,  variableProducers,  True, forceNonEmptySkim=True)

    if selection == "DisTrkSelection":
        add_channels  (process,  [disTrkSelectionNoD0CutNHits3],  histSets,        weights,  [],  collMap,  variableProducers,  False, forceNonEmptySkim=False, ignoreSkimmedCollections = True)
        add_channels  (process,  [disTrkSelectionSidebandD0CutNHits3],  histSets,        weights,  [],  collMap,  variableProducers,  False, forceNonEmptySkim=False, ignoreSkimmedCollections = True)
        add_channels  (process,  [disTrkSelectionSidebandD0CutNHits4],  histSets,        weights,  [],  collMap,  variableProducers,  False, forceNonEmptySkim=False, ignoreSkimmedCollections = True)        ...
        add_channels  (process,  [disTrkSelectionSidebandD0CutNHits5],  histSets,        weights,  [],  collMap,  variableProducers,  False, forceNonEmptySkim=False, ignoreSkimmedCollections = True)    if selection == "ZtoMuMu":
        add_channels  (process,  [disTrkSelectionSidebandD0CutNHits6],  histSets,        weights,  [],  collMap,  variableProducers,  False, forceNonEmptySkim=False, ignoreSkimmedCollections = True)        add_channels  (process,  [ZtoMuMu],                        histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers)

    if selection == "ZtoEE":
        add_channels  (process,  [ZtoEE],                           histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

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

    elif selection == "TriggerAnalysis":
        add_channels  (process,  [TauTagSkimSingleMuonTriggerSelection],         histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers + tauMETTriggerProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [TauTagSkimMuonTauTriggerSelection],  histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

    elif selection == "ElectronTagPt55":
        add_channels  (process,  [ElectronTagPt55],         histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronMETTriggerProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [ElectronTagPt55MetTrig],  histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

    elif selection == "ZtoEleProbeTrk":
        add_channels  (process,  [ZtoEleProbeTrk],                   histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

    elif selection == "ZtoMuProbeTrk":
        add_channels  (process,  [ZtoMuProbeTrk],                   histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + muonTPProducer)

    elif selection == "MuonTagPt55":
        add_channels  (process,  [MuonTagPt55],         histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + muonMETTriggerProducer)

    # Fiducial Maps
    elif selection == "MuonFiducial":
        add_channels  (process,  [MuonFiducialCalcBeforeOldCuts],  histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)
        add_channels  (process,  [MuonFiducialCalcAfterOldCuts],   histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

    elif selection == "ElectronFiducial":
        add_channels  (process,  [ElectronFiducialCalcBeforeOldCuts], histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True)
        add_channels  (process,  [ElectronFiducialCalcAfterOldCuts],  histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True, forceNonEmptySkim=True)

elif NLayers:
    if selection == "ZtoEE":
        add_channels  (process,  [ZtoEEDisTrkNoD0Cut],              histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True)
        add_channels  (process,  [ZtoEEDisTrkNoD0CutNLayers4],          histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers,  ignoreSkimmedCollections  =  True, forceNonEmptySkim=False)
        add_channels  (process,  getNLayersChannelVariations("ZtoEEDisTrkNoD0Cut"),              histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers, ignoreSkimmedCollections = True)

    elif selection == "MuonTagPt55":
        add_channels (process, getNHitsVariations("MuonTagPt55"),        histSetsMuon, weightsWithMuonSF, scaleFactorProducersWithMuons, collMap, variableProducers + muonMETTriggerProducer)
        add_channels (process, getNHitsVariations("MuonTagPt55MetTrig"), histSetsMuon, weightsWithMuonSF, scaleFactorProducersWithMuons, collMap, variableProducers + muonMETTriggerProducer)

    elif selection == "ZtoEleProbeTrk":
        add_channels  (process,  getNLayersChannelVariations("ZtoEleProbeTrk"),   histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=False)
        add_channels  (process,  getNLayersChannelVariations("ZtoEleProbeTrkWithFilter"),   histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=False)
        add_channels  (process,  getNLayersChannelVariations("ZtoEleProbeTrkWithSSFilter"), histSetsElectron,  weightsWithEleSF,  scaleFactorProducersWithElectrons,  collMap,  variableProducers + electronTPProducer, ignoreSkimmedCollections = True, forceNonEmptySkim=False)

    elif selection == "ZtoMuProbeTrk":
        add_channels  (process,  getNLayersChannelVariations("ZtoMuProbeTrk"),                   histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + muonTPProducer, ignoreSkimmedCollections = True)
        add_channels  (process,  getNLayersChannelVariations("ZtoMuProbeTrkWithFilter"),         histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + muonTPProducer, ignoreSkimmedCollections = True)
        add_channels  (process,  getNLayersChannelVariations("ZtoMuProbeTrkWithSSFilter"),       histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers + muonTPProducer, ignoreSkimmedCollections = True)

    elif selection == "ZtoMuMu":
        add_channels  (process,  getNLayersChannelVariations("ZtoMuMuDisTrkNoD0CutNLayers4"),            histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers, ignoreSkimmedCollections=True, forceNonEmptySkim=False)
        add_channels  (process,  getNLayersChannelVariations("ZtoMuMuDisTrkNoD0Cut"),       histSetsMuon,  weightsWithMuonSF,  scaleFactorProducersWithMuons,  collMap,  variableProducers)

    elif selection == "TauTagPt55":
        add_channels  (process,  getNLayersChannelVariations("TauTagPt55"),         histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers + tauMETTriggerProducer, ignoreSkimmedCollections=True)
        add_channels  (process,  getNLayersChannelVariations("TauTagPt55MetTrig"),  histSetsTau,  weights,  scaleFactorProducers,  collMap,  variableProducers, ignoreSkimmedCollections=True)

    elif selection == "ZtoTauToMuProbeTrk":
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
