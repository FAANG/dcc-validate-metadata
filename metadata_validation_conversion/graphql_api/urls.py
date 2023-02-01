from django.urls import path
from graphene_django.views import GraphQLView
from decouple import config
from django.views.decorators.csrf import csrf_exempt
from . import views

DEBUG = config('DEBUG', default=False)

app_name = 'graphql_api'
urlpatterns = [
    path("", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("download", views.download, name='download')
]