from django.contrib import admin
from .models import User
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'ip', 'device', 'count', 'insert_time', 'update_time')
    search_fields = ('ip',)
    readonly_fields = ('insert_time', 'update_time')


admin.site.register(User, UserAdmin)
