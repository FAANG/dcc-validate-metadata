from graphene import InputObjectType, String, Field, List


class RelatedDatasetsInputField(InputObjectType):
    accession = List(String)
    standardMet = List(String)
    species = List(String)


class ArticleFilterBasicArgument(InputObjectType):
    pmcId = List(String)
    pubmedId = List(String)
    doi = List(String)
    title = List(String)
    authorString = List(String)
    journal = List(String)
    issue = List(String)
    volume = List(String)
    year = List(String)
    pages = List(String)
    isOpenAccess = List(String)
    datasetSource = List(String)
    relatedDatasets = Field(RelatedDatasetsInputField)
    secondaryProject = List(String)


class ArticleFilterJoinArgument(InputObjectType):
    analysis = Field('graphql_api.grapheneObjects.analysis.arguments.filter.AnalysisFilterArgument')
    dataset = Field('graphql_api.grapheneObjects.dataset.arguments.filter.DatasetFilterArgument')
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')
    specimen = Field('graphql_api.grapheneObjects.specimen.arguments.filter.SpecimenFilterArgument')


class ArticleFilterArgument(InputObjectType):
    basic = Field(ArticleFilterBasicArgument)
    join = Field(ArticleFilterJoinArgument)
