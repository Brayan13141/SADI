from django.urls import path
from .views import crud_usuarios


urlpatterns = [
    path("admin/", crud_usuarios, name="gestion_usuarios"),
]
