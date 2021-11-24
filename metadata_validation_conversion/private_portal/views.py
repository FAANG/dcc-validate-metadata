import json

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from metadata_validation_conversion.settings import ES_USER, ES_PASSWORD

from elasticsearch import Elasticsearch, RequestsHttpConnection


class BovRegView(APIView):
    """
    Provides basic CRUD functions for the Blog Post model
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type):
        query = request.GET.get('q', '')
        es = Elasticsearch(
            ['elasticsearch-es-http:9200'],
            connection_class=RequestsHttpConnection,
            http_auth=(ES_USER, ES_PASSWORD),
            use_ssl=True, verify_certs=False)
        index = f'bovreg_{data_type}'
        if index == 'bovreg_file' or index == 'bovreg_dataset':
            sort = [{'private': {'order': 'desc'}}]
        else:
            sort = [{'releaseDate': {'order': 'desc'}}]
        if query != '':
            data = es.search(index=index, q=query)
        else:
            data = es.search(index=index, sort=sort, size=1000)
        return Response(data)


class BovRegDetailsView(APIView):
    """
    Provides details information
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type, item_id):
        es = Elasticsearch(
            ['elasticsearch-es-http:9200'],
            connection_class=RequestsHttpConnection,
            http_auth=(ES_USER, ES_PASSWORD),
            use_ssl=True, verify_certs=False)
        index = f'bovreg_{data_type}'
        data = es.search(index=index, q=f'_id:{item_id}')
        return Response(data)
