from django.urls import path
from . import views

app_name = 'trackhubs'
urlpatterns = [
    path('login/', views.login, name='login_webin'),
    path('validation/', views.validation, name='validate_trackhub'),
    path('submission/', views.submission, name='submit_trackhub')
]