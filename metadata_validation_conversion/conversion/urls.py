from django.urls import path

from . import views

urlpatterns = [
    path('samples', views.convert_samples, name='convert_samples'),
    path('experiments', views.convert_experiments, name='convert_experiments')
]