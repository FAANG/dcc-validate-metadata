from django.urls import path
from . import views

app_name = 'submission'
urlpatterns = [
    path('samples/<str:room_id>/<str:domain_action>', views.domain_actions,
         name='domain_actions'),
    path('<str:submission_type>/<str:task_id>/<str:room_id>/submit_records',
         views.submit_records, name='submit_records'),
    path('get_template/<str:task_id>/<str:room_id>/<str:data_type>',
         views.get_template, name='get_template'),
    path('download_template/<str:room_id>', views.download_template,
         name='download_template'),
    path('download_submission_results/<str:submission_type>/<str:task_id>',
         views.download_submission_results, name='download_submission_results')
]
