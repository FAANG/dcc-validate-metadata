from django.urls import path
from . import views

app_name = 'trackhubs'
urlpatterns = [
    path('register/', views.register_trackhub, name='register_trackhub'),
    path('upload/<str:genome_id>/<str:directory>', views.upload_tracks, name='upload_tracks'),
    path('upload/<str:genome_id>', views.upload_text_files, name='upload_text_files'),
]