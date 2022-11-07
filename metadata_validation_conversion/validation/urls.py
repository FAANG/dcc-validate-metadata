from django.urls import path

from . import views

app_name = 'validation'
urlpatterns = [
    path('<str:action>/<str:data_type>/<str:task_id>/<str:room_id>', views.validate,
         name='validate')
]
