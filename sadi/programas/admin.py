from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import ProgramaEstrategico, Ciclo

admin.site.register(ProgramaEstrategico, SimpleHistoryAdmin)
admin.site.register(Ciclo, SimpleHistoryAdmin)
