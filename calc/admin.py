from django.contrib import admin
from .models import CalcRecord, CalcParams, IrraParams, SmpParams, InputFilterParams

# Register your models here.


class CalcRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ip', 'device', 'file_path', 'cache_key', 'insert_time', 'update_time')
    search_fields = ('ip',)
    readonly_fields = ('insert_time', 'update_time')


class ParamsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'name', 'pin', 'file_path', 'uploader_email', 'insert_time', 'update_time')
    search_fields = ('name',)


admin.site.register(CalcRecord, CalcRecordAdmin)
admin.site.register(CalcParams, ParamsAdmin)
admin.site.register(IrraParams, ParamsAdmin)
admin.site.register(SmpParams, ParamsAdmin)
admin.site.register(InputFilterParams, ParamsAdmin)

