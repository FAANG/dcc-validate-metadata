from django.urls import path
from . import views

app_name = 'protocols_upload'
urlpatterns = [
    path('<str:protocol_type>', views.upload_protocol, name='upload_protocol'),
]
