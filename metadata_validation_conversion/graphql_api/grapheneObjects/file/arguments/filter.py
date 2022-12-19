from graphene import InputObjectType, String, Field, List


class SpeciesInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class FileExperimentInputField(InputObjectType):
    accession = List(String)
    target = List(String)
    assayType = List(String)
    standardMet = List(String)


class StudyInputField(InputObjectType):
    accession = List(String)
    alias = List(String)
    type = List(String)
    secondaryAccession = List(String)
    title = List(String)


class RunInputField(InputObjectType):
    accession = List(String)
    alias = List(String)
    platform = List(String)
    instrument = List(String)
    centerName = List(String)
    sequencingDate = List(String)
    sequencingLocation = List(String)
    sequencingLatitude = List(String)
    sequencingLongitude = List(String)


class FilePublishedArticlesInputField(InputObjectType):
    articleId = List(String)
    title = List(String)
    year = List(String)
    journal = List(String)
    pubmedId = List(String)
    doi = List(String)


class FileFilterBasicArgument(InputObjectType):
    # Use "Id" instead of "_id" in query as letter after _ is capitalized in GraphQL
    _id = List(String)
    specimen = List(String)
    organism = List(String)
    species = Field(SpeciesInputField)
    url = List(String)
    name = List(String)
    secondaryProject = List(String)
    type = List(String)
    size = List(String)
    readableSize = List(String)
    checksum = List(String)
    checksumMethod = List(String)
    archive = List(String)
    readCount = List(String)
    baseCount = List(String)
    releaseDate = List(String)
    updateDate = List(String)
    submission = List(String)
    experiment = Field(FileExperimentInputField)
    study = Field(StudyInputField)
    run = Field(RunInputField)
    paperPublished = List(String)
    publishedArticles = Field(FilePublishedArticlesInputField)
    submitterEmail = List(String)


class FileFilterJoinArgument(InputObjectType):
    experiment = Field('graphql_api.grapheneObjects.experiment.arguments.filter.ExperimentFilterArgument')
    article = Field('graphql_api.grapheneObjects.article.arguments.filter.ArticleFilterArgument')
    dataset = Field('graphql_api.grapheneObjects.dataset.arguments.filter.DatasetFilterArgument')
    organism = Field('graphql_api.grapheneObjects.organism.arguments.filter.OrganismFilterArgument')
    specimen = Field('graphql_api.grapheneObjects.specimen.arguments.filter.SpecimenFilterArgument')
    protocol_files = Field('graphql_api.grapheneObjects.protocol_files.arguments.filter.ProtocolFilesFilterArgument')
    protocol_samples = Field(
        'graphql_api.grapheneObjects.protocol_samples.arguments.filter.ProtocolSamplesFilterArgument')


class FileFilterArgument(InputObjectType):
    basic = Field(FileFilterBasicArgument)
    join = Field(FileFilterJoinArgument)
