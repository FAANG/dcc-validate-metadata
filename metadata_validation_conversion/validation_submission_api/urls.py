from django.urls import path
from . import views

app_name = 'validation_submission_api'
urlpatterns = [
    path('validation/<str:type>', views.validation, name='validate'),
    path('domain_actions/<str:domain_action>', views.domain_actions, name='domain_actions'),
    path('submission/<str:type>/<str:fileid>', views.submission, name='submit')
]