from graphene import Field, String, InputObjectType, List
from ...common_input_field_object import ProtocolInputField, UnitInputField


class CustomFieldInputField(InputObjectType):
    name = List(String)
    value = List(String)
    unit = List(String)
    ontologyTerms = List(String)


class ATACSeqInputField(InputObjectType):
    transposaseProtocol = Field(ProtocolInputField)


class BsSeqInputField(InputObjectType):
    librarySelection = List(String)
    bisulfiteConversionProtocol = Field(ProtocolInputField)
    pcrProductIsolationProtocol = Field(ProtocolInputField)
    bisulfiteConversionPercent = List(String)
    restrictionEnzyme = List(String)
    maxFragmentSizeSelectionRange = List(String)
    minFragmentSizeSelectionRange = List(String)


class ChIpSeqDnaBindingInputField(InputObjectType):
    chipProtocol = Field(ProtocolInputField)
    chipTarget = List(String)
    controlExperiment = List(String)
    chipAntibodyProvider = List(String)
    chipAntibodyCatalog = List(String)
    chipAntibodyLot = List(String)
    libraryGenerationMaxFragmentSizeRange = List(String)
    libraryGenerationMinFragmentSizeRange = List(String)


class ChipSeqInputDnaInputField(InputObjectType):
    chipProtocol = Field(ProtocolInputField)
    libraryGenerationMaxFragmentSizeRange = List(String)
    libraryGenerationMinFragmentSizeRange = List(String)


class DNaseSeqInputField(InputObjectType):
    dnaseProtocol = Field(ProtocolInputField)


class HiCInputField(InputObjectType):
    restrictionEnzyme = List(String)
    restrictionSite = List(String)
    hi_cProtocol = Field(ProtocolInputField)


class RnaSeqInputField(InputObjectType):
    rnaPreparation3AdapterLigationProtocol = Field(ProtocolInputField)
    rnaPreparation5AdapterLigationProtocol = Field(ProtocolInputField)
    libraryGenerationPcrProductIsolationProtocol = Field(ProtocolInputField)
    preparationReverseTranscriptionProtocol = Field(ProtocolInputField)
    libraryGenerationProtocol = Field(ProtocolInputField)
    readStrand = List(String)
    rnaPurity260280ratio = List(String)
    rnaPurity260230ratio = List(String)
    rnaIntegrityNumber = List(String)


class WgsInputField(InputObjectType):
    libraryGenerationPcrProductIsolationProtocol = Field(ProtocolInputField)
    libraryGenerationProtocol = Field(ProtocolInputField)
    librarySelection = List(String)


class CageSeqInputField(InputObjectType):
    cageProtocol = Field(ProtocolInputField)
    sequencingPrimerProvider = List(String)
    sequencingPrimerCatalog = List(String)
    sequencingPrimerLot = List(String)
    restrictionEnzymeTargetSequence = List(String)
    rnaPurity260280ratio = List(String)
    rnaPurity260230ratio = List(String)
    rnaIntegrityNumber = List(String)


class ExperimentFilterBasicArgument(InputObjectType):
    accession = List(String)
    accession = List(String)
    project = List(String)
    secondaryProject = List(String)
    assayType = List(String)
    experimentTarget = List(String)
    standardMet = List(String)
    versionLastStandardMet = List(String)
    libraryName = List(String)
    sampleStorage = List(String)
    sampleStorageProcessing = List(String)
    samplingToPreparationInterval = Field(UnitInputField)
    experimentalProtocol = Field(ProtocolInputField)
    extractionProtocol = Field(ProtocolInputField)
    libraryPreparationLocation = List(String)
    libraryPreparationLocationLatitude = Field(UnitInputField)
    libraryPreparationLocationLongitude = Field(UnitInputField)
    libraryPreparationDate = Field(UnitInputField)
    sequencingLocation = List(String)
    sequencingLocationLongitude = Field(UnitInputField)
    sequencingLocationLatitude = Field(UnitInputField)
    sequencingDate = Field(UnitInputField)
    customField = Field(CustomFieldInputField)
    ATACSeq = Field(ATACSeqInputField)
    BsSeq = Field(BsSeqInputField)
    ChIPSeqDnaBinding = Field(ChIpSeqDnaBindingInputField)
    HiC = Field(HiCInputField)
    RNASeq = Field(RnaSeqInputField)
    WGS = Field(WgsInputField)
    CAGESeq = Field(CageSeqInputField)

    ChIP_seq_input_DNA = Field(ChipSeqInputDnaInputField)
    DNase_seq = Field(DNaseSeqInputField)





class ExperimentFilterJoinArgument(InputObjectType):
    analysis = Field('graphql_api.grapheneObjects.analysis.arguments.filter.AnalysisFilterArgument')
    dataset = Field('graphql_api.grapheneObjects.dataset.arguments.filter.DatasetFilterArgument')
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')


class ExperimentFilterArgument(InputObjectType):
    basic = Field(ExperimentFilterBasicArgument)
    join = Field(ExperimentFilterJoinArgument)
