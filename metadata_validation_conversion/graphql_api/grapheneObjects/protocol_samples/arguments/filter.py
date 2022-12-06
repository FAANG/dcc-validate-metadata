from graphene import InputObjectType, String, Field, List


class SpecimensInputField(InputObjectType):
    id = List(String)
    organismPartCellType = List(String)
    organism = List(String)
    breed = List(String)
    derivedFrom = List(String)


class ProtocolSamplesFilterBasicArgument(InputObjectType):
    universityName = List(String)
    protocolDate = List(String)
    protocolName = List(String)
    key = List(String)
    url = List(String)
    specimens = Field(SpecimensInputField)


class ProtocolSamplesFilterJoinArgument(InputObjectType):
    organism = Field('graphql_api.grapheneObjects.organism.arguments.filter.OrganismFilterArgument')
    specimen = Field('graphql_api.grapheneObjects.specimen.arguments.filter.SpecimenFilterArgument')
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')


class ProtocolSamplesFilterArgument(InputObjectType):
    basic = Field(ProtocolSamplesFilterBasicArgument)
    join = Field(ProtocolSamplesFilterJoinArgument)
