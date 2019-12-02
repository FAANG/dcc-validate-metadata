from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('conversion/', include('conversion.urls')),
    path('validation/', include('validation.urls')),
    path('submission/', include('submission.urls')),
    path('admin/', admin.site.urls),
]