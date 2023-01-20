from graphene import Field, ObjectType, String, relay
from ..common_field_objects import ProtocolField


class ExperimentCustomFieldField(ObjectType):
    name = String()
    value = String()
    unit = String()
    ontologyTerms = String()


class ATACseqField(ObjectType):
    transposaseProtocol = Field(ProtocolField)


class BsSeqField(ObjectType):
    librarySelection = String()
    bisulfiteConversionProtocol = Field(ProtocolField)
    pcrProductIsolationProtocol = Field(ProtocolField)
    bisulfiteConversionPercent = String()
    restrictionEnzyme = String()
    maxFragmentSizeSelectionRange = String()
    minFragmentSizeSelectionRange = String()


class ChIPSeqDnaBindingField(ObjectType):
    chipProtocol = Field(ProtocolField)
    chipTarget = String()
    controlExperiment = String()
    chipAntibodyProvider = String()
    chipAntibodyCatalog = String()
    chipAntibodyLot = String()
    libraryGenerationMaxFragmentSizeRange = String()
    libraryGenerationMinFragmentSizeRange = String()


class ChIPseqInputDNAField(ObjectType):
    chipProtocol = Field(ProtocolField)
    libraryGenerationMaxFragmentSizeRange = String()
    libraryGenerationMinFragmentSizeRange = String()


class DNaseSeqField(ObjectType):
    dnaseProtocol = Field(ProtocolField)


class HiCField(ObjectType):
    restrictionEnzyme = String()
    restrictionSite = String()
    hiCProtocol = Field(ProtocolField)


class RNAseqField(ObjectType):
    rnaPreparation3AdapterLigationProtocol = Field(ProtocolField)
    rnaPreparation5AdapterLigationProtocol = Field(ProtocolField)
    libraryGenerationPcrProductIsolationProtocol = Field(ProtocolField)
    preparationReverseTranscriptionProtocol = Field(ProtocolField)
    libraryGenerationProtocol = Field(ProtocolField)
    readStrand = String()
    rnaPurity260280ratio = String()
    rnaPurity260230ratio = String()
    rnaIntegrityNumber = String()


class WGSField(ObjectType):
    libraryGenerationPcrProductIsolationProtocol = Field(ProtocolField)
    libraryGenerationProtocol = Field(ProtocolField)
    librarySelection = String()


class CAGEseqField(ObjectType):
    cageProtocol = Field(ProtocolField)
    sequencingPrimerProvider = String()
    sequencingPrimerCatalog = String()
    sequencingPrimerLot = String()
    restrictionEnzymeTargetSequence = String()
    rnaPurity260280ratio = String()
    rnaPurity260230ratio = String()
    rnaIntegrityNumber = String()


class ExperimentJoinField(ObjectType):
    analysis = relay.ConnectionField('graphql_api.grapheneObjects.analysis.schema.AnalysisConnection')
    dataset = relay.ConnectionField('graphql_api.grapheneObjects.dataset.schema.DatasetConnection')
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
