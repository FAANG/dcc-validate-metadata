from graphene import ObjectType, String, relay, Field, List
from ..commonFieldObjects import ProtocolField, OntologyField, UnitField


class SpecimenOrganizationField(ObjectType):
    name = String()
    role = String()
    URL = String()


class SpecimenCustomFieldField(ObjectType):
    name = String()
    value = String()
    unit = String()
    ontologyTerms = String()


class SpecimenOrganismField(ObjectType):
    biosampleId = String()
    organism = Field(OntologyField)
    sex = Field(OntologyField)
    breed = Field(OntologyField)
    healthStatus = List(of_type=OntologyField)


class SpecimenFromOrganismField(ObjectType):
    specimenCollectionDate = Field(UnitField)
    animalAgeAtCollection = Field(UnitField)
    developmentalStage = Field(OntologyField)
    healthStatusAtCollection = List(of_type=OntologyField)
    organismPart = Field(OntologyField)
    specimenCollectionProtocol = Field(ProtocolField)
    fastedStatus = String()
    numberOfPieces = Field(UnitField)
    specimenVolume = String()
    specimenSize = Field(UnitField)
    specimenWeight = Field(UnitField)
    specimenPictureUrl = List(String)
    gestationalAgeAtSampleCollection = Field(UnitField)


class PoolOfSpecimensField(ObjectType):
    poolCreationDate = Field(UnitField)
    poolCreationProtocol = Field(ProtocolField)
    specimenVolume = Field(UnitField)
    specimenSize = Field(UnitField)
    specimenWeight = Field(UnitField)
    specimenPictureUrl = String()


class CellSpecimenField(ObjectType):
    markers = String()
    cellType = Field(OntologyField)
    purificationProtocol = Field(ProtocolField)


class CellCultureField(ObjectType):
    cultureType = Field(OntologyField)
    cellType = Field(OntologyField)
    cellCultureProtocol = Field(ProtocolField)
    cultureConditions = String()
    numberOfPassages = String()


class CellLineField(ObjectType):
    organism = Field(OntologyField)
    sex = Field(OntologyField)
    cellLine = String()
    biomaterialProvider = String()
    catalogueNumber = String()
    numberOfPassages = String()
    dateEstablished = Field(UnitField)
    publication = String()
    breed = Field(OntologyField)
    cellType = Field(OntologyField)
    cultureConditions = String()
    cultureProtocol = Field(ProtocolField)
    disease = Field(OntologyField)
    karyotype = String()


class SpecimenPublishedArticlesField(ObjectType):
    articleId = String()
    title = String()
    year = String()
    journal = String()
    pubmedId = String()
    doi = String()


class SpecimenJoinField(ObjectType):
    analysis = relay.ConnectionField('graphql_api.grapheneObjects.analysis.schema.AnalysisConnection')
    article = relay.ConnectionField('graphql_api.grapheneObjects.article.schema.ArticleConnection')
    dataset = relay.ConnectionField('graphql_api.grapheneObjects.dataset.schema.DatasetConnection')
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
    protocol_samples = relay.ConnectionField(
        'graphql_api.grapheneObjects.protocol_samples.schema.ProtocolSamplesConnection')
    organism = relay.ConnectionField('graphql_api.grapheneObjects.organism.schema.OrganismConnection')
