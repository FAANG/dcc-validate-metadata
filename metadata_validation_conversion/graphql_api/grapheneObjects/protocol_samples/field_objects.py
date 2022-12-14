from graphene import ObjectType, String, relay


class SpecimensField(ObjectType):
    id = String()
    organismPartCellType = String()
    organism = String()
    breed = String()
    derivedFrom = String()


class ProtocolSamplesJoinField(ObjectType):
    organism = relay.ConnectionField('graphql_api.grapheneObjects.organism.schema.OrganismConnection')
    specimen = relay.ConnectionField('graphql_api.grapheneObjects.specimen.schema.SpecimenConnection')
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
    