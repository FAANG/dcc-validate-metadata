from django.urls import path
# from graphql_ws.django.consumers import GraphQLSubscriptionConsumer
# websocket_urlpatterns = [
#         path("subscriptions", CustomGraphQLSubscriptionConsumer.as_asgi())
#     ]

from graphql_ws.django.routing import websocket_urlpatterns