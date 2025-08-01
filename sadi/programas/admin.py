from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ProgramaEstrategico

admin.site.register(ProgramaEstrategico, SimpleHistoryAdmin)
