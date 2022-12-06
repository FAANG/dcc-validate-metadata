from django.urls import path
from graphene_django.views import GraphQLView
from decouple import config
from django.views.decorators.csrf import csrf_exempt
from . import views

DEBUG = config('DEBUG', default=False)

urlpatterns = [
    #  TODO remove csrf_exempt in prod : https://stackoverflow.com/questions/51764452/403-by-graphene-django-dont-use-csrf-exempt
    path("", csrf_exempt(GraphQLView.as_view(graphiql=DEBUG))),
    path("tasks/<str:task_id>", views.get_task_details)

]