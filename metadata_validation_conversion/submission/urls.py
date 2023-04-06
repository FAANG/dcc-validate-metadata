from django.urls import path
from . import views

app_name = 'submission'
urlpatterns = [
    path('samples/<str:room_id>/<str:domain_action>', views.domain_actions,
         name='domain_actions'),
    path('<str:action>/<str:submission_type>/<str:task_id>/<str:room_id>/submit_records',
         views.submit_records, name='submit_records'),
    path('submission_subscribe/<str:study_id>/<str:subscriber_email>',
         views.subscribe_studyid, name='subscribe_studyid'),
    path('submission_subscribe/<str:assay_type>/<str:secondary_project>/<str:subscriber_email>',
         views.subscribe_filtered_terms, name='subscribe_filtered_terms'),
    path('submission_unsubscribe/<str:study_id>/<str:subscriber_email>',
         views.submission_unsubscribe, name='submission_unsubscribe'),
    path('get_template/<str:task_id>/<str:room_id>/<str:data_type>',
         views.get_template, name='get_template'),
    path('download_template/<str:room_id>', views.download_template,
         name='download_template'),
    path('download_submission_results/<str:submission_type>/<str:task_id>',
         views.download_submission_results, name='download_submission_results')
]
