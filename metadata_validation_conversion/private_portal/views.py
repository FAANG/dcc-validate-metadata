import json

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from metadata_validation_conversion.settings import ES_USER, ES_PASSWORD, NODE

from elasticsearch import Elasticsearch, RequestsHttpConnection


class BovRegView(APIView):
    """
    Provides basic CRUD functions for the Blog Post model
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type):
        # Parse request parameters
        size = request.GET.get('size', 10)
        query = request.GET.get('q', '')
        from_ = request.GET.get('from_', 0)
        es = Elasticsearch([NODE], 
            connection_class=RequestsHttpConnection, 
            http_auth=(ES_USER, ES_PASSWORD), 
            use_ssl=True, verify_certs=False)
        index = f'bovreg_{data_type}'
        if index == 'bovreg_file' or index == 'bovreg_dataset':
            sort = 'private:desc'
        else:
            sort = 'releaseDate:desc'
        if query != '':
            data = es.search(index=index, from_=from_, size=size, sort=sort, q=query, track_total_hits=True)
        else:
            data = es.search(index=index, from_=from_, size=size, sort=sort, track_total_hits=True)
        return Response(data)


class BovRegDetailsView(APIView):
    """
    Provides details information
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type, item_id):
        es = Elasticsearch([NODE],
            connection_class=RequestsHttpConnection,
            http_auth=(ES_USER, ES_PASSWORD),
            use_ssl=True, verify_certs=False)
        index = f'bovreg_{data_type}'
        data = es.search(index=index, q=f'_id:{item_id}')
        return Response(data)
