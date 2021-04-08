from django.urls import path
from . import views

app_name = 'ontology_improver'
urlpatterns = [
    path('submit/', views.submit_ontology, name='submit_ontology'),
]