from django.urls import path

from .views import audit_url, home

urlpatterns = [
    path("", home, name="home"),
    path("api/audit", audit_url, name="audit-url"),
]
