from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Proyecto

admin.site.register(Proyecto, SimpleHistoryAdmin)
