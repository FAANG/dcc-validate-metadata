from django.urls import path
from . import views

app_name = 'submission'
urlpatterns = [
    path('samples/<str:task_id>', views.samples_submission,
         name='samples_submission'),
    path('experiments/<str:task_id>', views.experiments_submission,
         name='experiments_submission'),
    path('analyses/<str:task_id>', views.analyses_submission,
         name='analyses_submission')
]
