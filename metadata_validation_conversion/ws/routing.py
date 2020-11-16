from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/submission/(?P<task_id>\w+)/$', consumers.SubmissionConsumer.as_asgi()),
]
