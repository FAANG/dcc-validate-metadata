from graphene import InputObjectType, String, Field, List, Int
from ...common_input_field_object import ProtocolInputField, OntologyInputField, UnitInputField


class SpecimenOrganizationInputField(InputObjectType):
    name = List(String)
    role = List(String)
    URL = List(String)


class SpecimenCustomFieldInputField(InputObjectType):
    name = List(String)
    value = List(String)
    unit = List(String)
    ontologyTerms = List(String)


class SpecimenOrganismInputField(InputObjectType):
    biosampleId = List(String)
    organism = Field(OntologyInputField)
    sex = Field(OntologyInputField)
    breed = Field(OntologyInputField)
    healthStatus = Field(OntologyInputField)


class SpecimenFromOrganismInputField(InputObjectType):
    specimenCollectionDate = Field(UnitInputField)
    animalAgeAtCollection = Field(UnitInputField)
    developmentalStage = Field(OntologyInputField)
    healthStatusAtCollection = Field(OntologyInputField)
    organismPart = Field(OntologyInputField)
    specimenCollectionProtocol = Field(ProtocolInputField)
    fastedStatus = List(String)
    numberOfPieces = Field(UnitInputField)
    specimenVolume = List(String)
    specimenSize = Field(UnitInputField)
    specimenWeight = Field(UnitInputField)
    specimenPictureUrl = List(String)
    gestationalAgeAtSampleCollection = Field(UnitInputField)


class PoolOfSpecimensInputField(InputObjectType):
    poolCreationDate = Field(UnitInputField)
    poolCreationProtocol = Field(ProtocolInputField)
    specimenVolume = Field(UnitInputField)
    specimenSize = Field(UnitInputField)
    specimenWeight = Field(UnitInputField)
    specimenPictureUrl = List(String)


class CellSpecimenInputField(InputObjectType):
    markers = List(String)
    cellType = Field(OntologyInputField)
    purificationProtocol = Field(ProtocolInputField)


class CellCultureInputField(InputObjectType):
    cultureType = Field(OntologyInputField)
    cellType = Field(OntologyInputField)
    cellCultureProtocol = Field(ProtocolInputField)
    cultureConditions = List(String)
    numberOfPassages = List(String)


class CellLineInputField(InputObjectType):
    organism = Field(OntologyInputField)
    sex = Field(OntologyInputField)
    cellLine = List(String)
    biomaterialProvider = List(String)
    catalogueNumber = List(String)
    numberOfPassages = List(String)
    dateEstablished = Field(UnitInputField)
    publication = List(String)
    breed = Field(OntologyInputField)
    cellType = Field(OntologyInputField)
    cultureConditions = List(String)
    cultureProtocol = Field(ProtocolInputField)
    disease = Field(OntologyInputField)
    karyotype = List(String)


class SpecimenPublishedArticlesInputField(InputObjectType):
    articleId = List(String)
    title = List(String)
    year = List(String)
    journal = List(String)
    pubmedId = List(String)
    doi = List(String)


class SpecimenFilterBasicArgument(InputObjectType):
    biosampleId = List(String)
    id_number = List(Int)
    alternativeId = List(String)
    etag = List(String)
    name = List(String)
    description = List(String)
    releaseDate = List(String)
    updateDate = List(String)
    standardMet = List(String)
    versionLastStandardMet = List(String)
    project = List(String)
    secondaryProject = List(String)
    organization = Field(SpecimenOrganizationInputField)
    customField = Field(SpecimenCustomFieldInputField)
    material = Field(OntologyInputField)
    derivedFrom = List(String)
    allDeriveFromSpecimens = List(String)
    availability = List(String)
    cellType = Field(OntologyInputField)
    organism = Field(SpecimenOrganismInputField)
    specimenFromOrganism = Field(SpecimenFromOrganismInputField)
    poolOfSpecimens = Field(PoolOfSpecimensInputField)
    cellSpecimen = Field(CellSpecimenInputField)
    cellCulture = Field(CellCultureInputField)
    cellLine = Field(CellLineInputField)
    paperPublished = List(String)
    publishedArticles = Field(SpecimenPublishedArticlesInputField)
    trackhubUrl = List(String)


class SpecimenFilterJoinArgument(InputObjectType):
    analysis = Field('graphql_api.grapheneObjects.analysis.arguments.filter.AnalysisFilterArgument')
    article = Field('graphql_api.grapheneObjects.article.arguments.filter.ArticleFilterArgument')
    dataset = Field('graphql_api.grapheneObjects.dataset.arguments.filter.DatasetFilterArgument')
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')
    protocol_samples = Field(
        'graphql_api.grapheneObjects.protocol_samples.arguments.filter.ProtocolSamplesFilterArgument')
    organism = Field('graphql_api.grapheneObjects.organism.arguments.filter.OrganismFilterArgument')

class SpecimenFilterArgument(InputObjectType):
    basic = Field(SpecimenFilterBasicArgument)
    join = Field(SpecimenFilterJoinArgument)
