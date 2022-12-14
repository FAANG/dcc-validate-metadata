from graphene import ObjectType, String


class OntologyField(ObjectType):
    text = String()
    ontologyTerms = String()


class UnitField(ObjectType):
    text = String()
    unit = String()


class ProtocolField(ObjectType):
    url = String()
    filename = String()


class TaskResponse(ObjectType):
    id = String()
    status = String()
