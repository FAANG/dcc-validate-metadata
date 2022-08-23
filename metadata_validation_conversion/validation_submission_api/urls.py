from django.urls import path
from . import views

app_name = 'validation_submission_api'
urlpatterns = [
    path('validation/<str:type>', views.validation, name='validate'),
    path('submission/<str:type>', views.submission, name='submit')
]