from django.urls import path
from . import views

app_name = 'trackhubs'
urlpatterns = [
    path('<str:genome_id>/<str:directory>', views.upload_tracks, name='upload_tracks'),
    path('<str:genome_id>', views.upload_text_files, name='upload_text_files'),
]