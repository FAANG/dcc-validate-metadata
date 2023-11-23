from django.urls import path
from . import views
from django.conf.urls import url
from api.swagger_custom import schema_view

urlpatterns = [
    path('<str:name>/_search/', views.index, name='index'),
    path('_gsearch/', views.globindex, name='globindex'),
    path('<str:name>/<str:id>/update', views.update, name='update'),
    path('<str:name>/<str:id>', views.detail, name='detail'),
    path('<str:name>/download/', views.download, name='download'),
    path('fire_api/<str:protocol_type>/<str:id>', views.protocols_fire_api,
         name='protocols_fire_api'),
    path('summary', views.summary_api, name='summary'),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
