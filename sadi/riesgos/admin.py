from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Riesgo, Mitigacion

admin.site.register(Riesgo, SimpleHistoryAdmin)
admin.site.register(Mitigacion, SimpleHistoryAdmin)
