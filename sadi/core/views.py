from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from metas.models import Meta  # Ejemplo, importa tus modelos reales
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout, login
from django.shortcuts import render, redirect


@login_required
def dashboardView(request):
    return render(request, "core/dashboard.html")


def index(request):
    return render(request, "index.html")
