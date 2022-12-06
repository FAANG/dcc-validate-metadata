from graphene import InputObjectType, String, Field, List


class ExperimentsInputField(InputObjectType):
    accession = List(String)
    sampleStorage = List(String)
    sampleStorageProcessing = List(String)


class ProtocolFilesFilterBasicArgument(InputObjectType):
    name = List(String)
    experimentTarget = List(String)
    assayType = List(String)
    key = List(String)
    url = List(String)
    filename = List(String)
    experiments = Field(ExperimentsInputField)


class ProtocolFilesFilterJoinArgument(InputObjectType):
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')


class ProtocolFilesFilterArgument(InputObjectType):
    basic = Field(ProtocolFilesFilterBasicArgument)
    join = Field(ProtocolFilesFilterJoinArgument)
