import math
from collections import defaultdict
from .constants import MAX_FILTER_QUERY_DEPTH, index_mapping
import json
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection

es = Elasticsearch([settings.NODE],
                   connection_class=RequestsHttpConnection,
                   http_auth=(settings.ES_USER, settings.ES_PASSWORD),
                   use_ssl=True,
                   verify_certs=False)


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            for a in x:
                if type(a) is dict or type(a) is list:
                    flatten(a, name)
                else:
                    k = name[:-1]
                    if k in out:
                        out[k] = out[k] + ",\n" + ','.join(x)
                    else:
                        out[k] = ','.join(x)
                    return
        else:
            k = name[:-1]
            if x is None:
                x = ''
            if k in out:
                out[k] = out[k] + ",\n" + x
            else:
                out[k] = x

    flatten(y)
    return out


def add_id_to_document(document):
    _id = document['_id'] if '_id' in document else ''
    document = document['_source']
    document['_id'] = _id
    return document


def is_filter_query_depth_valid(filter, current_depth=1):
    if current_depth > MAX_FILTER_QUERY_DEPTH:
        return False
    if 'join' not in filter:
        return True

    filter_list = list(filter['join'])
    for right_index in filter_list:
        is_valid = is_filter_query_depth_valid(filter['join'][right_index], current_depth + 1)
        if not is_valid:
            return False
    return True


def generate_es_filters(basic_query, es_filter_queries, prefix=''):
    for key in list(basic_query):
        es_key = prefix + '.' + key if prefix else key
        if isinstance(basic_query[key], dict):
            generate_es_filters(basic_query[key], es_filter_queries, es_key)
        else:
            # if es_key not in non_keyword_properties:
            #     es_key += '.keyword'
            es_filter_queries.append({"terms": {es_key: basic_query[key]}})


# in-place editing, no need to return right_index_map
def update_experiment_fieldnames(right_index_map, mapping_key):
    key_value_list = right_index_map[mapping_key]

    for ele in key_value_list:
        if 'ChIP-seq DNA-binding' in ele:
            ele['ChIPSeqDnaBinding'] = ele.pop('ChIP-seq DNA-binding')
        if 'Hi-C' in ele:
            ele['HiC'] = ele.pop('Hi-C')
        if 'RNA-seq' in ele:
            ele['RNASeq'] = ele.pop('RNA-seq')
        if 'CAGE-seq' in ele:
            ele['CAGESeq'] = ele.pop('CAGE-seq')
        if 'ATAC-seq' in ele:
            ele['ATACSeq'] = ele.pop('ATAC-seq')
        if 'BS-seq' in ele:
            ele['BsSeq'] = ele.pop('BS-seq')


def update_experiment_es_fieldnames(dict_ele):
    if 'ChIPSeqDnaBinding' in dict_ele:
        dict_ele['ChIP-seq DNA-binding'] = dict_ele.pop('ChIPSeqDnaBinding')
    if 'HiC' in dict_ele:
        dict_ele['Hi-C'] = dict_ele.pop('HiC')
    if 'RNASeq' in dict_ele:
        dict_ele['RNA-seq'] = dict_ele.pop('RNASeq')
    if 'CAGESeq' in dict_ele:
        dict_ele['CAGE-seq'] = dict_ele.pop('CAGESeq')
    if 'ATACSeq' in dict_ele:
        dict_ele['ATAC-seq'] = dict_ele.pop('ATACSeq')
    if 'BsSeq' in dict_ele:
        dict_ele['BS-seq'] = dict_ele.pop('BsSeq')


def generate_index_map(index_data, record_key):
    index_map = defaultdict(list)
    for rec in index_data:
        mapping_keys_list = retrieve_mapping_keys(rec, record_key)

        for key in mapping_keys_list:
            if isinstance(key, list):
                for k in key:
                    index_map[k].append(rec)
            else:
                index_map[key].append(rec)

    return index_map


def retrieve_mapping_keys(record, record_key):
    flat_doc = flatten_json(record)
    mapping_keys = flat_doc.get(record_key, None)
    mapping_keys_list = []

    if mapping_keys:
        if '.' in record_key:
            mapping_keys_list = [*set(mapping_keys.split(',\n'))]
        else:
            mapping_keys_list = [*set(mapping_keys.split(','))]

    return mapping_keys_list


def get_projected_data(left_index, right_index, left_index_data, right_index_data):
    resultset = []

    right_index_map = generate_index_map(right_index_data,
                                         index_mapping[(left_index, right_index)]['right_index_key'])
    for left_document in left_index_data:
        if 'join' not in left_document:
            left_document['join'] = defaultdict(list)

        left_index_fk = index_mapping[(left_index, right_index)]['left_index_key']
        mapping_keys_list = retrieve_mapping_keys(left_document, left_index_fk)

        if mapping_keys_list:
            for key in mapping_keys_list:
                if key in right_index_map:
                    # exceptional case in experiment index where field name has space, e.g "ChIP-seq DNA-binding"
                    if right_index == "experiment":
                        update_experiment_fieldnames(right_index_map, key)

                    for rec in right_index_map[key]:
                        left_document['join'][right_index].append(rec)

        if not left_document['join'][right_index]:
            left_document['join'][right_index] = []

        resultset.append(left_document)

    return resultset


def fetch_with_join(filter, left_index, prev_index_data=None, key_filter_name=None):
    if prev_index_data is None:
        prev_index_data = []

    # query is invalid if we have a join between more than 3 indices
    if not is_filter_query_depth_valid(filter):
        raise Exception('Query exceeds the maximum join depth of {}'.format(MAX_FILTER_QUERY_DEPTH))

    if not bool(filter):
        return fetch_index_records(left_index)

    es_filter_queries = []
    if 'basic' in filter:
        # exceptional case in experiment index where field name has space, e.g "ChIP-seq DNA-binding"
        if left_index == "experiment":
            update_experiment_es_fieldnames(filter['basic'])
        generate_es_filters(filter['basic'], es_filter_queries)

    # if condition to deal with situation where Terms Query request exceeds the allowed maximum of [65536]
    if prev_index_data and len(prev_index_data) > 50000:
        left_index_data = []
        start_from = 0
        every_nth = 50000
        run_times = math.ceil(len(prev_index_data) / every_nth)
        for i in range(run_times):
            fetched_records = fetch_index_records(index_name=left_index, filter=es_filter_queries,
                                                  key_filter=prev_index_data[start_from:every_nth],
                                                  key_filter_name=key_filter_name)
            for dictionary in fetched_records:
                if dictionary not in left_index_data:
                    left_index_data.append(dictionary)

            start_from = every_nth
            every_nth = every_nth + 50000

    else:
        left_index_data = fetch_index_records(index_name=left_index, filter=es_filter_queries,
                                              key_filter=prev_index_data, key_filter_name=key_filter_name)

    # if left_index_data is empty (we cannot have join in this case)
    # or join not found in filter, return result of the left index only
    if not bool(left_index_data) or 'join' not in filter:
        return left_index_data

    for right_index in list(filter['join']):
        right_index_filter = filter['join'][right_index]

        mapping_key_list = []
        for rec in left_index_data:
            mapping_key_list.extend(retrieve_mapping_keys(rec,
                                                          index_mapping[(left_index, right_index)]['left_index_key']))

        right_index_data = fetch_with_join(right_index_filter, right_index,
                                           prev_index_data=mapping_key_list,
                                           key_filter_name=index_mapping[(left_index, right_index)][
                                               'right_index_key'])

        left_index_data = get_projected_data(left_index, right_index, left_index_data, right_index_data)

    # return the joined result data
    return left_index_data


def fetch_index_records(index_name, **kwargs):
    filter_queries = []
    if 'filter' in kwargs and kwargs['filter']:
        filter_queries.extend(kwargs['filter'])

    if 'key_filter' in kwargs and kwargs['key_filter'] and 'key_filter_name' in kwargs and kwargs['key_filter_name']:
        filter_queries.append({"terms": {kwargs['key_filter_name']: kwargs['key_filter']}})

    if filter_queries:
        query = {
            "query": {
                "bool": {
                    "filter": filter_queries
                }
            }
        }
    else:
        query = {
            "query": {
                'match_all': {}
            }
        }

    recordset = es_fetch_records(index_name, json.dumps(query))
    return recordset


def es_fetch_records(index, filters):
    count = 0
    recordset = []

    while True:
        res = es.search(index=index, size=50000, from_=count,
                        track_total_hits=True, body=json.loads(filters))
        count += 50000
        records = list(map(lambda rec: add_id_to_document(rec), res['hits']['hits']))
        recordset += records

        if count > res['hits']['total']['value']:
            break
    return recordset
