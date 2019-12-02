from django.urls import path
from . import views

app_name = 'conversion'
urlpatterns = [
    path('', views.index, name='index'),
    path('samples', views.convert_samples, name='convert_samples'),
    path('experiments', views.convert_experiments, name='convert_experiments'),
    path('analyses', views.convert_analyses, name='convert_analyses')
]
