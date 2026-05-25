from django.urls import path, re_path

from infrastructure.views import ApiView, DocsView, HomeView

urlpatterns = [
    re_path(r"^$", HomeView.as_view(), name="home"),
    path("docs/", DocsView.as_view(), name="docs"),
    path("api/", ApiView.as_view(), name="api"),
]
