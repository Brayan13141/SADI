from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Meta, AvanceMeta, MetaComprometida

admin.site.register(Meta, SimpleHistoryAdmin)
admin.site.register(AvanceMeta, SimpleHistoryAdmin)
admin.site.register(MetaComprometida, SimpleHistoryAdmin)
