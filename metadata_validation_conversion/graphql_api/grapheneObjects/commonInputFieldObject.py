from graphene import InputObjectType, List, String


class OntologyInputField(InputObjectType):
    text = List(String)
    ontologyTerms = List(String)


class UnitInputField(InputObjectType):
    text = List(String)
    unit = List(String)


class ProtocolInputField(InputObjectType):
    url = List(String)
    filename = List(String)
