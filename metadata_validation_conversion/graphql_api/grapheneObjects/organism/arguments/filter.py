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


class MaterialInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class OrganismInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class SexInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class BreedInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class BirthDateInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class HealthStatusInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class BirthLocationLongitudeInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class BirthLocationLatitudeInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class BirthWeightInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class PlacentalWeightInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class PregnancyLengthInputField(InputObjectType):
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
    material = Field(MaterialInputField)
    availability = List(String)
    organism = Field(OrganismInputField)
    sex = Field(SexInputField)
    breed = Field(BreedInputField)
    birthDate = Field(BirthDateInputField)
    healthStatus = Field(HealthStatusInputField)
    birthLocation = List(String)
    birthLocationLongitude = Field(BirthLocationLongitudeInputField)
    birthLocationLatitude = Field(BirthLocationLatitudeInputField)
    birthWeight = Field(BirthWeightInputField)
    placentalWeight = Field(PlacentalWeightInputField)
    pregnancyLength = Field(PregnancyLengthInputField)
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
