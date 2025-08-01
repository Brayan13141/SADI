from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ObjetivoEstrategico

admin.site.register(ObjetivoEstrategico, SimpleHistoryAdmin)
