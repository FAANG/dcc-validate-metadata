from django.urls import path
from . import views

app_name = 'trackhubs'
urlpatterns = [
    path('register/', views.register_trackhub, name='register_trackhub'),
    path('upload/<str:hub_dir>/<str:genome>/<str:sub_dir>', views.upload_tracks, name='upload_tracks'),
    path('upload/<str:hub_dir>/<str:genome>', views.upload_text_files, name='upload_text_files'),
]