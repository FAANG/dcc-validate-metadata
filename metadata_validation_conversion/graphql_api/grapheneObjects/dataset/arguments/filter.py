from graphene import InputObjectType, String, Field, List
from ...commonInputFieldObject import OntologyInputField


class SpecimenInputField(InputObjectType):
    biosampleId = List(String)
    material = Field(OntologyInputField)
    cellType = Field(OntologyInputField)
    sex = Field(OntologyInputField)
    breed = Field(OntologyInputField)


class FileInputField(InputObjectType):
    url = List(String)
    name = List(String)
    fileId = List(String)
    experiment = List(String)
    type = List(String)
    size = List(String)
    readableSize = List(String)
    archive = List(String)
    readCount = List(String)
    baseCount = List(String)
    checksumMethod = List(String)
    checksum = List(String)


class DatasetExperimentInputField(InputObjectType):
    accession = List(String)
    target = List(String)
    assayType = List(String)


class DatasetPublishedArticlesInputField(InputObjectType):
    articleId = List(String)
    title = List(String)
    year = List(String)
    journal = List(String)


class DatasetFilterBasicArgument(InputObjectType):
    accession = List(String)
    standardMet = List(String)
    secondaryProject = List(String)
    title = List(String)
    alias = List(String)
    assayType = List(String)
    tech = List(String)
    secondaryAccession = List(String)
    archive = List(String)
    specimen = Field(SpecimenInputField)
    # specimen = List(of_type=SpecimenInputField)
    species = Field(OntologyInputField)
    # species = List(of_type=OntologyInputField)
    releaseDate = List(String)
    updateDate = List(String)
    file = Field(FileInputField)
    experiment = Field(DatasetExperimentInputField)
    instrument = List(String)
    centerName = List(String)
    paperPublished = List(String)
    publishedArticles = Field(DatasetPublishedArticlesInputField)
    submitterEmail = List(String)


class DatasetFilterJoinArgument(InputObjectType):
    experiment = Field('graphql_api.grapheneObjects.experiment.arguments.filter.ExperimentFilterArgument')
    article = Field('graphql_api.grapheneObjects.article.arguments.filter.ArticleFilterArgument')
    analysis = Field('graphql_api.grapheneObjects.analysis.arguments.filter.AnalysisFilterArgument')
    specimen = Field('graphql_api.grapheneObjects.specimen.arguments.filter.SpecimenFilterArgument')
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')


class DatasetFilterArgument(InputObjectType):
    basic = Field(DatasetFilterBasicArgument)
    join = Field(DatasetFilterJoinArgument)
