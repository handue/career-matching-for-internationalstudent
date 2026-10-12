"""Route Django web requests to apps. / Django 웹 요청을 앱에 연결합니다."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("jobs.urls")),
]
