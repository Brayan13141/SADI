from django.urls import path
from .views import dashboardView, index

urlpatterns = [
    path("", dashboardView, name="dashboard"),
]
