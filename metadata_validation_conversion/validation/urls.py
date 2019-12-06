from django.urls import path

from . import views

app_name = 'validation'
urlpatterns = [
    path('samples/<str:task_id>/<str:room_id>', views.validate_samples,
         name='validate_samples'),
    path('experiments/<str:task_id>/<str:room_id>', views.validate_experiments,
         name='validate_experiments'),
    path('analyses/<str:task_id>/<str:room_id>', views.validate_analyses,
         name='validate_analyses')
]
