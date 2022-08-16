from django.urls import path
from . import views

app_name = 'validation_submission_api'
urlpatterns = [
    path('validation/', views.validation, name='validate'),
    path('submission/', views.submission, name='submit')
]