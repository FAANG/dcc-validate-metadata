from django.urls import path
from . import views

app_name = 'conversion'
urlpatterns = [
    path('<str:task_id>', views.convert_template, name='convert_template')
]
