from graphene import ObjectType, String, relay

class RelatedDatasets_Field(ObjectType):
    accession = String()
    standardMet = String()
    species = String()

class ArticleJoin_Field(ObjectType):
    analysis = relay.ConnectionField('graphql_api.grapheneObjects.analysis.schema.AnalysisConnection')
    dataset = relay.ConnectionField('graphql_api.grapheneObjects.dataset.schema.DatasetConnection')
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
    specimen = relay.ConnectionField('graphql_api.grapheneObjects.specimen.schema.SpecimenConnection')