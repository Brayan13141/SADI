from django.urls import path
from .views import dashboard, cambiar_ciclo_flecha

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("cambiar_ciclo_flecha/", cambiar_ciclo_flecha, name="cambiar_ciclo_flecha"),
]
