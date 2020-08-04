from django.urls import path
from . import views

app_name = 'submission'
urlpatterns = [
    path('samples/<str:room_id>/choose_domain', views.choose_domain,
         name='choose_domain'),
    path('samples/<str:room_id>/submit_domain', views.submit_domain,
         name='submit_domain'),
    path('samples/<str:task_id>/<str:room_id>/submit_records',
         views.submit_records,
         name='submit_records'),
    path('samples/<str:task_id>/<str:room_id>', views.samples_conversion,
         name='samples_submission'),
    path('experiments/<str:task_id>/<str:room_id>', views.experiments_submission,
         name='experiments_submission'),
    path('analyses/<str:task_id>/<str:room_id>', views.analyses_submission,
         name='analyses_submission'),
    path('get_data/<str:task_id>', views.send_data, name='send_data'),
    path('get_template/<str:task_id>/<str:room_id>/<str:data_type>',
         views.get_template, name='get_template'),
    path('download_template/<str:room_id>', views.download_template,
         name='download_template'),
    path('download_submission_results/<str:task_id>',
         views.download_submission_results, name='download_submission_results')
]
