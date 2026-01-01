from django.contrib import admin
from django.urls import path, include

from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]), name="swagger-ui"),

    path("api/auth/", include("accounts.urls")),
    path("api/", include("assessments.urls")),
    path("api/", include("submissions.urls")),
]
