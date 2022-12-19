from graphene import InputObjectType, String, Field, List
from ...common_input_field_object import ProtocolInputField


class FilesInputField(InputObjectType):
    name = List(String)
    url = List(String)
    type = List(String)
    size = List(String)
    checksumMethod = List(String)
    checksum = List(String)


class AnalysisDateInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class AnalysisOrganismInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class AnalysisFilterBasicArgument(InputObjectType):
    accession = List(String)
    project = List(String)
    secondaryProject = List(String)
    title = List(String)
    alias = List(String)
    description = List(String)
    standardMet = List(String)
    versionLastStandardMet = List(String)
    releaseDate = List(String)
    updateDate = List(String)
    organism = Field(AnalysisOrganismInputField)
    type = List(String)
    datasetAccession = List(String)
    datasetInPortal = List(String)
    sampleAccessions = List(String)
    experimentAccessions = List(String)
    runAccessions = List(String)
    analysisAccessions = List(String)
    files = Field(FilesInputField)
    analysisDate = Field(AnalysisDateInputField)
    assayType = List(String)
    analysisProtocol = Field(ProtocolInputField)
    analysisType = List(String)
    referenceGenome = List(String)
    analysisCenter = List(String)
    analysisCodeRepository = List(String)
    experimentType = List(String)
    program = List(String)
    platform = List(String)
    imputation = List(String)


class AnalysisFilterJoinArgument(InputObjectType):
    experiment = Field('graphql_api.grapheneObjects.experiment.arguments.filter.ExperimentFilterArgument')
    article = Field('graphql_api.grapheneObjects.article.arguments.filter.ArticleFilterArgument')
    dataset = Field('graphql_api.grapheneObjects.dataset.arguments.filter.DatasetFilterArgument')
    specimen = Field('graphql_api.grapheneObjects.specimen.arguments.filter.SpecimenFilterArgument')
    protocol_analysis = Field('graphql_api.grapheneObjects.protocol_analysis.arguments.filter'
                              '.ProtocolAnalysisFilterArgument')

class AnalysisFilterArgument(InputObjectType):
    basic = Field(AnalysisFilterBasicArgument)
    join = Field(AnalysisFilterJoinArgument)
