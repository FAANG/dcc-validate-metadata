from graphene import ObjectType, String, relay


class AnalysesField(ObjectType):
    accession = String()
    organism = String()
    datasetAccession = String()
    analysisType = String()


class ProtocolAnalysisJoinField(ObjectType):
    analysis = relay.ConnectionField('graphql_api.grapheneObjects.analysis.schema.AnalysisConnection')
