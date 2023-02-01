from django.contrib import admin
from django.urls import include, path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    path('conversion/', include('conversion.urls')),
    path('validation/', include('validation.urls')),
    path('submission/', include('submission.urls')),
    path('protocols_upload/', include('protocols_upload.urls')),
    path('private_portal/', include('private_portal.urls')),
    path('ontology_improver/', include('ontology_improver.urls')),
    path('trackhub/', include('trackhubs.urls')),
    path('nextflow_upload/', include('nextflow_upload.urls')),
    path('validation_submission_api/', include('validation_submission_api.urls')),
    path('graphql/', include('graphql_api.urls')),
    path('admin_panel/', admin.site.urls),
    path('data/', include('api.urls')),
    path(r'api-token-auth/', obtain_jwt_token),
    path(r'api-token-refresh/', refresh_jwt_token)
]
