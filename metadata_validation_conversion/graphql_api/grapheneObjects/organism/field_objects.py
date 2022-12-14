from graphene import ObjectType, String, relay

class FileOrganizationField(ObjectType):
    name = String()
    role = String()
    URL = String()

class OrganismCustomFieldField(ObjectType):
    name = String()
    value = String()
    unit = String()
    ontologyTerms = String()

class Material_Field(ObjectType):
    text = String()
    ontologyTerms = String()

class Organism_Field(ObjectType):
    text = String()
    ontologyTerms = String()

class Sex_Field(ObjectType):
    text = String()
    ontologyTerms = String()

class Breed_Field(ObjectType):
    text = String()
    ontologyTerms = String()

class BirthDate_Field(ObjectType):
    text = String()
    unit = String()

class HealthStatusField(ObjectType):
    text = String()
    ontologyTerms = String()

class BirthLocationLongitude_Field(ObjectType):
    text = String()
    unit = String()

class BirthLocationLatitude_Field(ObjectType):
    text = String()
    unit = String()

class BirthWeight_Field(ObjectType):
    text = String()
    unit = String()

class PlacentalWeight_Field(ObjectType):
    text = String()
    unit = String()

class PregnancyLength_Field(ObjectType):
    text = String()
    unit = String()

class OrganismPublishedArticles_Field(ObjectType):
    articleId = String()
    title = String()
    year = String()
    journal = String()

class OrganismJoin_Field(ObjectType):
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
    specimen = relay.ConnectionField('graphql_api.grapheneObjects.specimen.schema.SpecimenConnection')
    protocol_samples = relay.ConnectionField('graphql_api.grapheneObjects.protocol_samples.schema.ProtocolSamplesConnection')