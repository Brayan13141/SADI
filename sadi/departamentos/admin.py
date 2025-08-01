from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Departamento

admin.site.register(Departamento, SimpleHistoryAdmin)
