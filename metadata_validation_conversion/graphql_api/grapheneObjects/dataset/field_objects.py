from graphene import ObjectType, String, relay, Field
from ..commonFieldObjects import OntologyField


class SpecimenField(ObjectType):
    biosampleId = String()
    material = Field(OntologyField)
    cellType = Field(OntologyField)
    organism = Field(OntologyField)
    sex = Field(OntologyField)
    breed = Field(OntologyField)


class FileField(ObjectType):
    url = String()
    name = String()
    fileId = String()
    experiment = String()
    type = String()
    size = String()
    readableSize = String()
    archive = String()
    readCount = String()
    baseCount = String()
    checksumMethod = String()
    checksum = String()


class DatasetExperimentField(ObjectType):
    accession = String()
    target = String()
    assayType = String()


class DatasetPublishedArticlesField(ObjectType):
    articleId = String()
    title = String()
    year = String()
    journal = String()


class DatasetJoinField(ObjectType):
    experiment = relay.ConnectionField('graphql_api.grapheneObjects.experiment.schema.ExperimentConnection')
    article = relay.ConnectionField('graphql_api.grapheneObjects.article.schema.ArticleConnection')
    analysis = relay.ConnectionField('graphql_api.grapheneObjects.analysis.schema.AnalysisConnection')
    specimen = relay.ConnectionField('graphql_api.grapheneObjects.specimen.schema.SpecimenConnection')
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
