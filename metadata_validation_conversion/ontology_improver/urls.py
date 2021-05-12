from django.urls import path
from . import views

app_name = 'ontology_improver'
urlpatterns = [
    path('auth/', views.authentication, name='authentication'),
    path('search/', views.search_terms, name='search_terms'),
    path('get_matches/', views.get_zooma_ontologies, name='get_zooma_ontologies'),
    path('validate/', views.validate_terms, name='validate_terms')
]