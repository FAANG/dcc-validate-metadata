from django.urls import path
from . import views

app_name = 'ontology_improver'
urlpatterns = [
    path('auth/', views.authentication, name='authentication'),
    path('register/', views.registration, name='registration'),
    path('search/', views.search_terms, name='search_terms'),
    path('get_matches/', views.get_zooma_ontologies, name='get_zooma_ontologies'),
    path('validate/', views.validate_terms, name='validate_terms'),
    path('summary/', views.summary, name='summary'),
    path('update_ontologies/', views.ontology_updates, name='ontology_updates'),
    path('update_summary/', views.summary_updates, name='summary_updates'),
    path('ontology_detail/<str:id>', views.get_ontology_details, name='ontology_detail')
]