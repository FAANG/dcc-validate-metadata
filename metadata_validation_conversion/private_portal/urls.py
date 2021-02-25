from django.urls import path, include
from rest_framework import routers

from . import views

urlpatterns = [
    path('<str:data_type>/', views.BovRegView.as_view(),
         name='private_data'),
    path('<str:data_type>/<str:item_id>/', views.BovRegDetailsView.as_view(),
         name='private_data_details')
]
