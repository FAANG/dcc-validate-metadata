import requests
import json

from django.http import JsonResponse, HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import cache

from .helpers import generate_df, generate_df_for_breeds
from .constants import FIELD_NAMES, HUMAN_READABLE_NAMES
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import AllowAny
from api.swagger_custom import TextFileRenderer, PdfFileRenderer
from api.swagger_custom import HTMLAutoSchema, PlainTextAutoSchema, PdfAutoSchema
from api.swagger_custom import index_search_request_example, \
    index_search_response_example, index_detail_response_example

ALLOWED_INDICES = ['file', 'organism', 'specimen', 'dataset', 'experiment',
                   'protocol_files', 'protocol_samples', 'article',
                   'protocol_analysis', 'analysis', 'summary_organism',
                   'summary_specimen', 'summary_dataset', 'summary_file']


@swagger_auto_schema(method='get', tags=['Search'],
        operation_summary="Get a list of Organisms, Specimens, Files, Datasets etc",
        manual_parameters=[
            openapi.Parameter('size', openapi.IN_QUERY, 
                description="no. of records to fetch", 
                type=openapi.TYPE_NUMBER, default=10),
            openapi.Parameter('_source', openapi.IN_QUERY, 
                description="fields (comma-separated) to fetch", 
                type=openapi.TYPE_STRING),
            openapi.Parameter('sort', openapi.IN_QUERY, 
                description="field to sort on, with :asc or :desc appended \
                    to specify order, eg - id:asc", 
                type=openapi.TYPE_STRING),
            openapi.Parameter('q', openapi.IN_QUERY, 
                description="advanced queries", 
                type=openapi.TYPE_STRING),
            openapi.Parameter('from_', openapi.IN_QUERY, 
                description="to fetch records starting from specified number", 
                type=openapi.TYPE_NUMBER, default=0),
            openapi.Parameter('filters', openapi.IN_QUERY, 
                description="properties and list of values to filter on, \
                    in the format {prop1: [val1, val2], prop2: [val1, val2], ...} ", 
                type=openapi.TYPE_STRING, default='{}'),
            openapi.Parameter('aggs', openapi.IN_QUERY, 
                description="aggregation names and properties on which \
                    to aggregate, in the format - {aggName1: prop1, aggName2: prop2, ...}", 
                type=openapi.TYPE_STRING, default='{}'),
            openapi.Parameter('name', openapi.IN_PATH, 
                description="type of records to fetch",
                type=openapi.TYPE_STRING,
                enum=ALLOWED_INDICES)
        ],
        responses={
            200: openapi.Response(description='OK', 
                examples={"application/json": index_search_response_example},
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: openapi.Response('Not Found')
        })
@swagger_auto_schema(method='post', tags=['Search'],
        operation_summary="Advanced Search for Organisms, Specimens, Files, Datasets etc",
        operation_description="Advanced search using elasticsearch queries",
        manual_parameters=[
            openapi.Parameter('size', openapi.IN_QUERY, 
                description="no. of records to fetch", 
                type=openapi.TYPE_NUMBER, default=10),
            openapi.Parameter('name', openapi.IN_PATH, 
                description="type of records to fetch",
                type=openapi.TYPE_STRING,
                enum=ALLOWED_INDICES)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, 
            example=index_search_request_example
        ),
        responses={
            200: openapi.Response('OK',
                examples={"application/json": index_search_response_example},
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: openapi.Response('Not Found')
        })
@api_view(['GET','POST'])
@permission_classes([AllowAny])
@csrf_exempt
def index(request, name):
    if request.method != 'GET' and request.method != 'POST':
        context = {
            'status': '405', 'reason': 'This method is not allowed!'  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 405
        return response
    if name not in ALLOWED_INDICES:
        context = {
            'status': '404', 'reason': 'This index doesn\'t exist!'  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 404
        return response

    # Parse request parameters
    size = request.GET.get('size', 10)
    field = request.GET.get('_source', '')
    sort = request.GET.get('sort', '')
    query = request.GET.get('q', '')
    from_ = request.GET.get('from_', 0)
    # Example: {field1: [val1, val2], field2: [val1, val2], ...}
    filters = request.GET.get('filters', '{}')    
    # Example: {aggName1: field1, aggName2: field2, ...}  
    aggregations = request.GET.get('aggs', '{}')    

    # generate query for filtering
    filter_values = []
    not_filter_values = []
    filters = json.loads(filters)
    for key in filters.keys():
        if filters[key][0] != 'false':
            filter_values.append({"terms": {key: filters[key]}})
        else:
            not_filter_values.append({"terms": {key: ["true"]}})
    filter_val = {}
    if filter_values:
        filter_val['must'] = filter_values
    if not_filter_values:
        filter_val['must_not'] = not_filter_values
    if filter_val:
        filters = {"query": {"bool": filter_val}}

    # generate query for aggregations
    agg_values = {}
    aggregations = json.loads(aggregations)
    for key in aggregations.keys():
        # size determines number of aggregation buckets returned
        agg_values[key] = {"terms": {"field": aggregations[key], "size": 25}} 
        if key == 'paper_published':
            # aggregations for missing paperPublished field
            agg_values["paper_published_missing"] = {
                "missing": {"field": "paperPublished"}}

    filters['aggs'] = agg_values

    set_cache = False
    data = None

    # Get cache if request goes to file or specimen
    # if int(size) == 100000 and query == '':
    #     cache_key = "{}_key".format(name)
    #     cache_time = 86400
    #     data = cache.get(cache_key)
    #     set_cache = True

    if not data:
        es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=False)
        if request.body:
            data = es.search(index=name, size=size, body=json.loads(
                request.body.decode("utf-8")))
        else:
            if query != '':
                data = es.search(index=name, from_=from_, size=size, _source=field,
                                 sort=sort, q=query, body=filters)
            else:
                data = es.search(index=name, from_=from_, size=size, _source=field,
                                 sort=sort, body=filters)
        if set_cache:
            cache.set(cache_key, data, cache_time)

    return JsonResponse(data)

@swagger_auto_schema(method='put', tags=['Update'],
        operation_summary="Update records",
        operation_description="Update records by queries",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_PATH, 
                description="type of records to query",
                type=openapi.TYPE_STRING,
                enum=ALLOWED_INDICES),
            openapi.Parameter('id', openapi.IN_PATH, 
                description="id of record to update",
                type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, 
            example=index_search_request_example
        ),
        responses={
            200: openapi.Response('Updated',
                examples={"application/json": index_search_response_example},
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: openapi.Response('Not Found')
        })
@api_view(['PUT'])
@permission_classes([AllowAny])
@csrf_exempt
def update(request, name, id):
    if request.method != 'PUT':
        context = {
            'status': '405', 'reason': 'This method is not allowed!'  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 405
        return response
    if name not in ALLOWED_INDICES:
        context = {
            'status': '404', 'reason': 'This index doesn\'t exist!'  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 404
        return response    

    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=False)
    if request.body:
        print(request.body.decode("utf-8"))
        data = es.update(index=name, id=id, doc_type="_doc",
            body=json.loads(request.body.decode("utf-8")))
        return JsonResponse(data)


@swagger_auto_schema(method='get', tags=['Details'],
        operation_summary="Get details of the Organism, Specimen, File or Dataset etc, by their ID",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_PATH, 
                description="type of record",
                type=openapi.TYPE_STRING,
                enum=ALLOWED_INDICES),
            openapi.Parameter('id', openapi.IN_PATH, 
                description="id of the record",
                type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('OK',
                examples={"application/json": index_detail_response_example},
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: openapi.Response('Not Found')
        })
@api_view(['GET'])
@csrf_exempt
def detail(request, name, id):
    if request.method != 'GET':
        context = {
            'status': '405', 'reason': 'This method is not allowed!'  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 405
        return response
    if name not in ALLOWED_INDICES:
        context = {
            'status': '404', 'reason': 'This index doesn\'t exist!'  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 404
        return response
    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=False)
    results = es.search(index=name, q="_id:{}".format(id))
    if results['hits']['total'] == 0:
        results = es.search(index=name, q="alternativeId:{}".format(id),
                            doc_type="_doc")
    if results['hits']['total'] == 0:
        results = es.search(index=name, q="biosampleId:{}".format(id),
                            doc_type="_doc")
    return JsonResponse(results)


@swagger_auto_schema(method='get', tags=['Protocols'],
        auto_schema=PdfAutoSchema,
        operation_summary="Get protocol file",
        manual_parameters=[
            openapi.Parameter('protocol_type', openapi.IN_PATH, 
                description="type of protocol",
                type=openapi.TYPE_STRING,
                enum=['samples','experiments','analyses','analysis','assays']),
            openapi.Parameter('id', openapi.IN_PATH, 
                description="id of the protocol file",
                type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('OK', 
                schema=openapi.Schema(type=openapi.TYPE_FILE)),
            404: openapi.Response('Not Found')
        })
@api_view(['GET'])
@renderer_classes([PdfFileRenderer])
def protocols_fire_api(request, protocol_type, id):
    url = "https://{}.fire.sdo.ebi.ac.uk/fire/public/faang/ftp/protocols/" \
          "{}/{}".format(settings.DATACENTER, protocol_type, id)
    res = requests.get(url)
    if res.status_code == 200:
        file = res.content
        response = HttpResponse(file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(id)
        return response
    else:
        return HttpResponse(status=404)


@swagger_auto_schema(method='get', tags=['Trackhubs'],
        auto_schema=PlainTextAutoSchema,
        operation_summary="Get trackhubs by doc ID",
        manual_parameters=[
            openapi.Parameter('doc_id', openapi.IN_PATH, 
                description="Document ID",
                type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('OK', 
                schema=openapi.Schema(type=openapi.TYPE_FILE)),
            404: openapi.Response('Not Found')
        })
@api_view(['GET'])
@renderer_classes([TextFileRenderer])
def trackhubregistry_fire_api(request, hub_dir, doc_id):
    url = "https://{}.fire.sdo.ebi.ac.uk/fire/public/faang/ftp/" \
          "trackhubregistry/{}/{}".format(settings.DATACENTER, hub_dir, doc_id)
    res = requests.get(url)
    if res.status_code == 200:
        file = res.content
        response = HttpResponse(file, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(doc_id)
        return response
    else:
        return HttpResponse(status=404)


@swagger_auto_schema(method='get', tags=['Trackhubs'],
        auto_schema=PlainTextAutoSchema,
        operation_summary="Get trackhubs by Genome and doc ID",
        manual_parameters=[
            openapi.Parameter('genome_id', openapi.IN_PATH, 
                description="Genome ID",
                type=openapi.TYPE_STRING),
            openapi.Parameter('doc_id', openapi.IN_PATH, 
                description="Document ID",
                type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('OK', 
                schema=openapi.Schema(type=openapi.TYPE_FILE)),
            404: openapi.Response('Not Found')
        })
@api_view(['GET'])
@renderer_classes([TextFileRenderer])
def trackhubregistry_with_dir_fire_api(request, hub_dir, genome_id, doc_id):
    url = "https://{}.fire.sdo.ebi.ac.uk/fire/public/faang/ftp/" \
          "trackhubregistry/{}/{}/{}".format(settings.DATACENTER, hub_dir, genome_id,
                                          doc_id)
    res = requests.get(url)
    if res.status_code == 200:
        file = res.content
        response = HttpResponse(file, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(doc_id)
        return response
    else:
        return HttpResponse(status=404)


@swagger_auto_schema(method='get', tags=['Trackhubs'],
        auto_schema=PlainTextAutoSchema,
        operation_summary="Get trackhubs by Genome ID, folder and doc ID",
        manual_parameters=[
            openapi.Parameter('genome_id', openapi.IN_PATH, 
                description="Genome ID",
                type=openapi.TYPE_STRING),
            openapi.Parameter('folder', openapi.IN_PATH, 
                description="Folder name",
                type=openapi.TYPE_STRING),
            openapi.Parameter('doc_id', openapi.IN_PATH, 
                description="Document ID",
                type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response('OK', 
                schema=openapi.Schema(type=openapi.TYPE_FILE)),
            404: openapi.Response('Not Found')
        })
@api_view(['GET'])
@renderer_classes([TextFileRenderer])
def trackhubregistry_with_dirs_fire_api(request, hub_dir, genome_id, folder, doc_id):
    url = "https://{}.fire.sdo.ebi.ac.uk/fire/public/faang/ftp/" \
          "trackhubregistry/{}/{}/{}/{}".format(settings.DATACENTER, hub_dir, genome_id,
                                             folder, doc_id)
    res = requests.get(url)
    if res.status_code == 200:
        file = res.content
        response = HttpResponse(file, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(doc_id)
        return response
    else:
        return HttpResponse(status=404)


@swagger_auto_schema(method='get', tags=['Summary'],
        auto_schema=HTMLAutoSchema,
        operation_summary="Get summary of all FAANG Data",
        responses={
            200: openapi.Response('OK',
                schema=openapi.Schema(type=openapi.TYPE_STRING))
        })
@api_view(['GET'])
def summary_api(request):
    final_results = ''
    for item in FIELD_NAMES.keys():
        data = requests.get(
            "https://data.faang.org/api/summary_{}/summary_{}".format(
                item, item)).json()
        data = data['hits']['hits'][0]['_source']
        results = list()
        results_faang_only = list()
        for field_name in FIELD_NAMES[item]:
            if 'breed' in field_name:
                tmp, tmp_faang_only = generate_df_for_breeds(
                    field_name, HUMAN_READABLE_NAMES[field_name], data)
            else:
                tmp, tmp_faang_only = generate_df(field_name,
                                                  HUMAN_READABLE_NAMES[
                                                      field_name], data)
            results.append(tmp)
            results_faang_only.append(tmp_faang_only)
        final_results += '<h1>{} Summary</h1>'.format(item.capitalize())
        final_results += '<br>'
        final_results += '<h3>FAANG only data</h3>'
        final_results += '<br>'
        for table in results_faang_only:
            final_results += table.to_html(index=False)
            final_results += '<br>'
        final_results += '<h3>All data</h3>'
        final_results += '<br>'
        for table in results:
            final_results += table.to_html(index=False)
            final_results += '<br>'
        final_results += '<br>'
        final_results += '<hr>'
    return HttpResponse(final_results)
