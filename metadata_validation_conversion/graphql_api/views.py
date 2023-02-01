from django.http import HttpResponse
from graphql_api.grapheneObjects.helpers import flatten_json
import requests
import json
import csv


def download(request):
    # Request params
    selected_indices = request.GET.get('selected_indices', '[]')
    selected_columns = request.GET.get('selected_columns', '')
    query_name = request.GET.get('query_name', '')
    query_string = request.GET.get('query', '')
    query = f'{json.loads(query_string)}'
    url = 'https://api.faang.org/graphql/'
    res = requests.post(url, json={'query': query})

    if res and res.status_code == 200:
        graphql_res = json.loads(res.text)
        records_list = graphql_res['data'][json.loads(query_name)]['edges']
        complete_resultset = []
        join_records = []
        join_index = ''

        for record in records_list:
            join_obj = record['node']['join']
            left_index_obj = {k: v for k, v in record['node'].items() if k != 'join'}
            if join_obj:
                join_index = next(iter(join_obj))
                join_records = join_obj[join_index]['edges'];

            data_table = []

            flat_left_index_obj = \
                {f'{json.loads(selected_indices)[0]}.' + key: value
                 for key, value in flatten_json(left_index_obj).items()}

            if join_records and len(join_records) > 0:
                for rec in join_records:
                    flat_rec = flatten_json(rec['node'])
                    updated_flat_rec = {f'{join_index}.' + key: value for key, value in flat_rec.items()}
                    container = flat_left_index_obj | updated_flat_rec
                    data_table.append(container)
            else:
                # no joinRecords associated with right index
                data_table.append(flat_left_index_obj)

            complete_resultset.extend(data_table)

        # generate response payload
        filename = 'faang-join-data.csv'
        content_type = 'text/csv'
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=' + filename

        # generate csv data
        columns = json.loads(selected_columns)
        writer = csv.DictWriter(response, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(complete_resultset)
        return response
