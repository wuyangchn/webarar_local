from django.contrib import admin
from .models import Journal, CUGJournalRanking

# Register your models here.


class JournalAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'short_name', 'jif21', 'jif22', 'jif23', 'category', 'issn', 'eissn')
    search_fields = ('full_name',)


class CUGJournalRankingAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'tier', 'jif21', 'jif22', 'jif23', 'tag', 'subject', 'short_name', 'issn', 'eissn')
    search_fields = ('full_name',)


admin.site.register(Journal, JournalAdmin)
admin.site.register(CUGJournalRanking, CUGJournalRankingAdmin)
