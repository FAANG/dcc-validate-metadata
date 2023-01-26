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


class TextOntologyTermsField(ObjectType):
    text = String()
    ontologyTerms = String()


class TextUnitField(ObjectType):
    text = String()
    unit = String()


class OrganismPublishedArticlesField(ObjectType):
    articleId = String()
    title = String()
    year = String()
    journal = String()


class OrganismJoinField(ObjectType):
    file = relay.ConnectionField('graphql_api.grapheneObjects.file.schema.FileConnection')
    specimen = relay.ConnectionField('graphql_api.grapheneObjects.specimen.schema.SpecimenConnection')
    protocol_samples = relay.ConnectionField(
        'graphql_api.grapheneObjects.protocol_samples.schema.ProtocolSamplesConnection')
