import requests
import json
import os

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
import csv

ALLOWED_INDICES = ['file', 'organism', 'specimen', 'dataset', 'experiment',
                   'protocol_files', 'protocol_samples', 'article',
                   'protocol_analysis', 'analysis', 'summary_organism',
                   'summary_specimen', 'summary_dataset', 'summary_file',
                   'ensembl_annotation', 'trackhubs', 'submissions', 
                   'ontologies', 'summary_ontologies', 'submission_portal_status',
                   'ontologies_test', 'summary_ontologies_test'
                   ]

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
    sort_by_count = request.GET.get('sort_by_count', '')
    query = request.GET.get('q', '')
    search = request.GET.get('search', '')
    from_ = request.GET.get('from_', 0)
    # Example: {field1: [val1, val2], field2: [val1, val2], ...}
    filters = request.GET.get('filters', '{}')
    # Example: {aggName1: field1, aggName2: field2, ...}
    aggregations = request.GET.get('aggs', '{}')
    body = {}

    # generate query for filtering
    filter_values = []
    not_filter_values = []
    filters = json.loads(filters)
    for key in filters.keys():
        # status_activity filter is a special case because the status property
        # is found within status_activity arrau of objects
        if key == 'status_activity':
            nested_query_body = {
                "nested": {
                    "path": "status_activity",
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "status_activity.status": filters[key][0]
                                    }
                                }
                            ]
                        }
                    }
                }}
            filter_values.append(nested_query_body)
        else:
            if filters[key][0] != 'false':
                filter_values.append({"terms": {key: filters[key]}})
            else:
                not_filter_values.append({"match": {key: "true"}})
    filter_val = {}
    if filter_values:
        filter_val['must'] = filter_values
    if not_filter_values:
        filter_val['must_not'] = not_filter_values

    if filter_val:
        body['query'] = {'bool': filter_val}

    # generate query for search
    if search:
        match = {
            'multi_match': {
                'query': search,
                'fields': ['*']
            }
        }
        if filter_val:
            if 'must' in filter_val:
                body['query']['bool']['must'].append(match)
            else:
                body['query']['bool']['must'] = [match]
        else:
            body['query'] = {
                'bool': {
                    'must': [match]
                }
            }

    # generate query for aggregations
    agg_values = {}
    aggregations = json.loads(aggregations)
    for key in aggregations.keys():
        # status_activity aggregation is a special case because the status property is a nested property
        if key == 'status_activity':
            agg_values[key] = {
                "nested": {
                    "path": "status_activity"
                },
                "aggs": {
                    "status": {
                        "terms": {
                            "field": "status_activity.status", 'size': 25
                        }
                    }
                }
            }
        else:
            # size determines number of aggregation buckets returned
            agg_values[key] = {"terms": {"field": aggregations[key], "size": 25}}
            if key == 'paper_published':
                # aggregations for missing paperPublished field
                agg_values["paper_published_missing"] = {
                    "missing": {"field": "paperPublished"}}

    if agg_values:
        body['aggs'] = agg_values

    # generate query for sort script
    # sorts by length of field array
    if sort_by_count:
        sort_field, order = sort_by_count.split(':')
        body['sort'] = {
            "_script": {
                "type": "number",
                "script": f"params._source?.{sort_field}?.length ?: 0",
                "order": f"{order}"
            }
        }

    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)
    if request.body:
        data = es.search(index=name, size=size, body=json.loads(
            request.body.decode("utf-8"), track_total_hits=True))
    else:
        if query != '':
            data = es.search(index=name, from_=from_, size=size, _source=field,
                                sort=sort, q=query, body=body, track_total_hits=True)
        else:
            data = es.search(index=name, from_=from_, size=size, _source=field,
                                sort=sort, body=body, track_total_hits=True)

    return JsonResponse(data)

@swagger_auto_schema(method='put', auto_schema=None, tags=['Update'],
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

    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)
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
    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)
    id = f"\"{id}\""
    results = es.search(index=name, q="_id:{}".format(id))
    if results['hits']['total'] == 0:
        results = es.search(index=name, q="alternativeId:{}".format(id),
                            doc_type="_doc")
    if results['hits']['total'] == 0:
        results = es.search(index=name, q="biosampleId:{}".format(id),
                            doc_type="_doc")
    return JsonResponse(results)


@swagger_auto_schema(method='get', tags=['Download'],
        operation_summary="Get a list of Organisms, Specimens, Files, Datasets etc",
        manual_parameters=[
            openapi.Parameter('columns_names', openapi.IN_QUERY, 
                description="List of column headers", 
                type=openapi.TYPE_STRING, default='[]'),
            openapi.Parameter('file_format', openapi.IN_QUERY, 
                description="csv or tabular text file", 
                type=openapi.TYPE_STRING, default='csv'),
            openapi.Parameter('_source', openapi.IN_QUERY, 
                description="fields (comma-separated) to fetch", 
                type=openapi.TYPE_STRING),
            openapi.Parameter('sort', openapi.IN_QUERY, 
                description="field to sort on, with :asc or :desc appended \
                    to specify order, eg - id:asc", 
                type=openapi.TYPE_STRING),
            openapi.Parameter('filters', openapi.IN_QUERY, 
                description="properties and list of values to filter on, \
                    in the format {prop1: [val1, val2], prop2: [val1, val2], ...} ", 
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
@api_view(['GET'])
@csrf_exempt
def download(request, name):
    if request.method != 'GET':
        return HttpResponse("This method is not allowed!\n")
    if name not in ALLOWED_INDICES:
        return HttpResponse("This download doesn't exist!\n")

    # Request params
    file_format = request.GET.get('file_format', '')
    field = request.GET.get('_source', '')
    column_names = request.GET.get('columns', '[]')
    sort = request.GET.get('sort', '')
    filters = request.GET.get('filters', '{}')

    columns = field.split(',')
    request_fields = []
    for col in columns:
        cols = col.split('.')
        if cols[0] == '_source':
            request_fields.append('.'.join(cols[1:]))
    request_fields = ','.join(request_fields)
    column_names = json.loads(column_names)

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

    # Get records from elasticsearch
    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)
    count = 0
    records = []
    while True:
        data = es.search(index=name, _source=request_fields, sort=sort, 
                        body=filters, from_=count, size=10000, track_total_hits=True)
        hits = data['hits']['hits']
        records += hits
        count += 10000
        if count > data['hits']['total']['value']:
            break

    # generate response payload
    if file_format == 'csv':
        filename = 'faang_data.csv'
        content_type = 'text/csv'
    else:
        filename = 'faang_data.txt'
        content_type = 'text/plain'
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # generate csv data
    writer = csv.DictWriter(response, fieldnames=columns)
    headers = {}
    i = 0
    for col in columns:
        headers[col] = column_names[i]
        i += 1
    writer.writerow(headers)
    for row in records:
        record = {}
        for col in columns:
            cols = col.split('.')
            record[col] = ''
            source = row
            for c in cols:
                if  isinstance(source, dict) and c in source.keys():
                    record[col] = source[c]
                    source = source[c]
                else:
                    record[col] = ''
                    break
        writer.writerow(record)

    # return formatted data
    if file_format == 'csv':
        return response
    else:
        # add padding to align with max length data in a column
        def space(i, d):
            max_len = len(max(list(zip(*row_data))[i], key=len))
            return d+' '*(max_len-len(d))

        # create fixed width and '|' separated tabular text file
        data = response.content
        lines = [i.rstrip(b'\r\n') for i in filter(None, data.split(b'\n'))]
        lines = [line.decode("utf-8") for line in lines]
        row_data = csv.reader(lines, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        row_data = list(row_data)
        tab_rows = [' | '.join(space(*c) for c in enumerate(b)) for b in row_data]
        tab_data = '\n'.join(tab_rows)
        response.content = tab_data
        return response

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
    cmd = f"aws --no-sign-request --endpoint-url" \
            f" http://{settings.DATACENTER}.fire.sdo.ebi.ac.uk" \
                 f" s3 cp s3://faang-public/ftp/protocols/{protocol_type}/{id} ./"
    os.system(cmd)
    file_location = f"./{id}"
    try:    
        with open(file_location, 'rb') as f:
           file_data = f.read()
        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(id)
        return response
    except IOError:
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
            "https://apifaang.org.uk/summary_{}/summary_{}".format(
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
