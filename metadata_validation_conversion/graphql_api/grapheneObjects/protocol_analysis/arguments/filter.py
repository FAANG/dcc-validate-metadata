from graphene import InputObjectType, String, Field, List


class AnalysesInputField(InputObjectType):
    accession = List(String)
    organism = List(String)
    datasetAccession = List(String)
    analysisType = List(String)


class AnalysisProtocolInputField(InputObjectType):
    url = List(String)
    filename = List(String)


class ProtocolAnalysisFilterBasicArgument(InputObjectType):
    universityName = List(String)
    protocolDate = List(String)
    protocolName = List(String)
    key = List(String)
    url = List(String)
    analyses = Field(AnalysesInputField)


class ProtocolAnalysisFilterJoinArgument(InputObjectType):
    analysis = Field('graphql_api.grapheneObjects.analysis.arguments.filter.AnalysisFilterArgument')


class ProtocolAnalysisFilterArgument(InputObjectType):
    basic = Field(ProtocolAnalysisFilterBasicArgument)
    join = Field(ProtocolAnalysisFilterJoinArgument)
