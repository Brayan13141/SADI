from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Usuario

admin.site.register(Usuario, SimpleHistoryAdmin)
