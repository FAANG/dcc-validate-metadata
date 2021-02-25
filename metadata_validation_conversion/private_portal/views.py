import json

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from elasticsearch import Elasticsearch


class BovRegView(APIView):
    """
    Provides basic CRUD functions for the Blog Post model
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type):
        es = Elasticsearch(['elasticsearch-master-headless:9200'])
        index = 'bovreg_organism' if data_type == 'organism' \
            else 'bovreg_specimen'
        data = es.search(index=index, sort='releaseDate:desc', size=1000)
        return Response(data)


class BovRegDetailsView(APIView):
    """
    Provides details information
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type, item_id):
        es = Elasticsearch(['elasticsearch-master-headless:9200'])
        index = 'bovreg_organism' if data_type == 'organism' \
            else 'bovreg_specimen'
        data = es.search(index=index, q=f'_id:{item_id}')
        return Response(data)
