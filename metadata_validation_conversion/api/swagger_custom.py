
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import renderers

# openAPI schema
class SchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super(SchemaGenerator, self).get_schema(request, public)
        schema.basePath = os.path.join(schema.basePath, 'data/')
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="FAANG API",
        default_version='1.0',
        description='API to access FAANG Data'
    ),
    public=True,
    urlconf='api.urls',
    generator_class=SchemaGenerator,
)

# response renderers
class TextFileRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'text'
    def render(self, data, media_type=None, renderer_context=None):
        return str(renderers.JSONRenderer().render(data, media_type, renderer_context)).encode(self.charset)

class PdfFileRenderer(renderers.BaseRenderer):
    media_type = 'application/pdf'
    format = 'byte'
    def render(self, data, media_type=None, renderer_context=None):
        return str(renderers.JSONRenderer().render(data, media_type, renderer_context)).encode(self.charset)

# response schemas
class HTMLAutoSchema(SwaggerAutoSchema):
    def get_produces(self):
        return ["text/html"]

class PlainTextAutoSchema(SwaggerAutoSchema):
    def get_produces(self):
        return ["text/plain"]
        
class PdfAutoSchema(SwaggerAutoSchema):
    def get_produces(self):
        return ["application/pdf"]

# response examples
index_search_response_example = {
    "took": 2,
    "timed_out": "false",
    "_shards": {
        "total": 5,
        "successful": 5,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "hits": [
            {
                "prop1": "val1_1", 
                "prop2": "val2_1"
            },
            {
                "prop1": "val1_2", 
                "prop2": "val2_2"
            }
        ]
    },
}

index_detail_response_example = {
    "took": 2,
    "timed_out": "false",
    "_shards": {
        "total": 5,
        "successful": 5,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "hits": [
            {
                "prop1": "val1_1", 
                "prop2": "val2_1"
            }
        ]
    },
}

# request example
index_search_request_example = {
	"query": {
		"bool": {
			"filter": [{
					"term": {
						"standardMet": "FAANG"
					}
				},
				{
					"term": {
						"organism.sex.text": "female"
					}
				},
				{
					"term": {
						"organism.organism.text": "Equus caballus"
					}
				},
				{
					"term": {
						"material.text": "specimen from organism"
					}
				},
				{
					"term": {
						"cellType.text": "liver left lateral lobe"
					}
				}
			]
		}
	}
}