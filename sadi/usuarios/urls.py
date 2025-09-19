from django.urls import path
from .views import gestion_usuarios


urlpatterns = [
    path("admin/", gestion_usuarios, name="gestion_usuarios"),
]
