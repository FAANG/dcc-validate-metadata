from graphene import InputObjectType, String, Field, Int, List


class OrganismOrganizationInputField(InputObjectType):
    name = List(String)
    role = List(String)
    URL = List(String)


class OrganismCustomFieldInputField(InputObjectType):
    name = List(String)
    value = List(String)
    unit = List(String)
    ontologyTerms = List(String)


class TextOntologyTermsInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class TextUnitInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class OrganismPublishedArticlesInputField(InputObjectType):
    articleId = List(String)
    title = List(String)
    year = List(String)
    journal = List(String)


class OrganismFilterBasicArgument(InputObjectType):
    biosampleId = List(String)
    id_number = List(Int)
    alternativeId = List(String)
    etag = List(String)
    name = List(String)
    description = List(String)
    releaseDate = List(String)
    updateDate = List(String)
    standardMet = List(String)
    versionLastStandardMet = List(String)
    project = List(String)
    secondaryProject = List(String)
    organization = Field(OrganismOrganizationInputField)
    customField = Field(OrganismCustomFieldInputField)
    material = Field(TextOntologyTermsInputField)
    availability = List(String)
    organism = Field(TextOntologyTermsInputField)
    sex = Field(TextOntologyTermsInputField)
    breed = Field(TextOntologyTermsInputField)
    birthDate = Field(TextUnitInputField)
    healthStatus = Field(TextOntologyTermsInputField)
    birthLocation = List(String)
    birthLocationLongitude = Field(TextUnitInputField)
    birthLocationLatitude = Field(TextUnitInputField)
    birthWeight = Field(TextUnitInputField)
    placentalWeight = Field(TextUnitInputField)
    pregnancyLength = Field(TextUnitInputField)
    deliveryTiming = List(String)
    deliveryEase = List(String)
    childOf = List(String)
    pedigree = List(String)
    paperPublished = List(String)
    publishedArticles = Field(OrganismPublishedArticlesInputField)


class OrganismFilterJoinArgument(InputObjectType):
    file = Field('graphql_api.grapheneObjects.file.arguments.filter.FileFilterArgument')
    specimen = Field('graphql_api.grapheneObjects.specimen.arguments.filter.SpecimenFilterArgument')
    protocol_samples = Field(
        'graphql_api.grapheneObjects.protocol_samples.arguments.filter.ProtocolSamplesFilterArgument')


class OrganismFilterArgument(InputObjectType):
    basic = Field(OrganismFilterBasicArgument)
    join = Field(OrganismFilterJoinArgument)
