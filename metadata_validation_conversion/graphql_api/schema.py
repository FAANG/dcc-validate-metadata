from graphene import Schema, String, relay, ObjectType, Field
from .grapheneObjects.organism.schema import OrganismSchema
from .grapheneObjects.analysis.schema import AnalysisSchema
from .grapheneObjects.experiment.schema import ExperimentSchema
from .grapheneObjects.dataset.schema import DatasetSchema
from .grapheneObjects.file.schema import FileSchema
from .grapheneObjects.article.schema import ArticleSchema
from .grapheneObjects.specimen.schema import SpecimenSchema
from .grapheneObjects.protocol_analysis.schema import ProtocolAnalysisSchema
from .grapheneObjects.protocol_samples.schema import ProtocolSamplesSchema
from .grapheneObjects.protocol_files.schema import ProtocolFilesSchema


class Query(OrganismSchema, ExperimentSchema, AnalysisSchema, ArticleSchema, DatasetSchema, FileSchema, SpecimenSchema,
            ProtocolAnalysisSchema, ProtocolFilesSchema, ProtocolSamplesSchema):
    pass


schema = Schema(query=Query)
