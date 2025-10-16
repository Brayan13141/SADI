from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Meta


admin.site.register(Meta, SimpleHistoryAdmin)
