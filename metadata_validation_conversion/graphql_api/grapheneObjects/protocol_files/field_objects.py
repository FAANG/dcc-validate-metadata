from graphene import ObjectType, String, relay


class ExperimentsField(ObjectType):
    accession = String()
    sampleStorage = String()
    sampleStorageProcessing = String()


class ProtocolFilesJoinField(ObjectType):
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
