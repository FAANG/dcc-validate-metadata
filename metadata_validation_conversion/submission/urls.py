from django.urls import path
from . import views

app_name = 'submission'
urlpatterns = [
    path('samples', views.samples_submission, name='samples_submission'),
    path('experiments', views.experiments_submission,
         name='experiments_submission'),
    path('analyses', views.analyses_submission, name='analyses_submission')
]