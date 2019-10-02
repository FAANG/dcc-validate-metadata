from django.urls import path

from . import views

app_name = 'validation'
urlpatterns = [
    path('samples/<str:task_id>', views.validate_samples,
         name='validate_samples'),
]
