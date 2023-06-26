from django.urls import path
from . import views

app_name = 'submission'
urlpatterns = [
    path('samples/<str:room_id>/<str:domain_action>', views.domain_actions,
         name='domain_actions'),
    path('<str:action>/<str:submission_type>/<str:task_id>/<str:room_id>/submit_records',
         views.submit_records, name='submit_records'),
    path('submission_subscribe_faang/<str:index_name>/<str:index_pk>/<str:subscriber_email>',
         views.filtered_subscription, name='filtered_subscription'),
    path('submission_unsubscribe/<str:study_id>/<str:subscriber_email>',
         views.submission_unsubscribe, name='submission_unsubscribe'),
    path('subscription_email/<str:study_id>/<str:subscriber_email>',
         views.subscription_email, name='subscription_email'),
    path('get_template/<str:task_id>/<str:room_id>/<str:data_type>',
         views.get_template, name='get_template'),
    path('download_template/<str:room_id>', views.download_template,
         name='download_template'),
    path('download_submission_results/<str:submission_type>/<str:task_id>',
         views.download_submission_results, name='download_submission_results')
]
