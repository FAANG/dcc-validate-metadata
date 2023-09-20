from django.urls import path
from . import views

app_name = 'ontology_improver_workshop'
urlpatterns = [
    path('auth/', views.authentication, name='authentication'),
    path('register/', views.registration, name='registration'),
    path('get_matches/', views.get_zooma_ontologies, name='get_zooma_ontologies'),
    path('validate/', views.validate_ontology, name='validate_ontology'),
    path('update_ontologies/', views.ontology_updates, name='ontology_updates')
]