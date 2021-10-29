from django.urls import path, include
from rest_framework import routers

from . import views

urlpatterns = [
    path('<str:data_type>/', views.OrganismsView.as_view(),
         name='private_data'),
]
