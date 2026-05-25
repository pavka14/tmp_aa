from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from .views import ConnectionViewSet, DeviceViewSet, InterfaceViewSet, SiteViewSet

router = DefaultRouter()
router.register(r"sites", SiteViewSet, basename="site")
router.register(r"devices", DeviceViewSet, basename="device")
router.register(r"interfaces", InterfaceViewSet, basename="interface")
router.register(r"connections", ConnectionViewSet, basename="connection")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
