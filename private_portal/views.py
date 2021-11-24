import json

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response


class OrganismsView(APIView):
    """
    Provides basic CRUD functions for the Blog Post model
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, data_type):
        data = list()
        return Response(data)
