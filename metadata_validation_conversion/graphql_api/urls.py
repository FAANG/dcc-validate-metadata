from django.urls import path
from graphene_django.views import GraphQLView
from decouple import config
from django.views.decorators.csrf import csrf_exempt
from . import views

DEBUG = config('DEBUG', default=False)

urlpatterns = [
    path("", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("tasks/<str:task_id>", views.get_task_details)

]