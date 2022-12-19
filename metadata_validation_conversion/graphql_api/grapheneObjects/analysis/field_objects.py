from graphene import ObjectType, String, relay


class FilesField(ObjectType):
    name = String()
    url = String()
    type = String()
    size = String()
    checksumMethod = String()
    checksum = String()


class AnalysisDateField(ObjectType):
    text = String()
    unit = String()


class AnalysisOrganismField(ObjectType):
    text = String()
    ontologyTerms = String()


class AnalysisJoinField(ObjectType):
    experiment = relay.ConnectionField('graphql_api.grapheneObjects.experiment.schema.ExperimentConnection')
    article = relay.ConnectionField('graphql_api.grapheneObjects.article.schema.ArticleConnection')
    dataset = relay.ConnectionField('graphql_api.grapheneObjects.dataset.schema.DatasetConnection')
    specimen = relay.ConnectionField('graphql_api.grapheneObjects.specimen.schema.SpecimenConnection')
    protocol_analysis = relay.ConnectionField('graphql_api.grapheneObjects.protocol_analysis.schema'
                                              '.ProtocolAnalysisConnection')
