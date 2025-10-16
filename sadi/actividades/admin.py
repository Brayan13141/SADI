from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Actividad, SolicitudReapertura, Evidencia


admin.site.register(Actividad, SimpleHistoryAdmin)
admin.site.register(SolicitudReapertura, SimpleHistoryAdmin)
admin.site.register(Evidencia, SimpleHistoryAdmin)
