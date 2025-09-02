from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import render


@login_required
def dashboardView(request):
    return render(request, "core/dashboard.html")


def index(request):
    return render(request, "index.html")
