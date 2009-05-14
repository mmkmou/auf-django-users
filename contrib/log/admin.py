# -*- encoding: utf-8 -*-

from models import Log
from django.contrib import admin

class LogAdmin(admin.ModelAdmin):
    list_display = ( 'username_creation', 'colored_type', 'details', 'date', 'agent')
    ordering = ( '-date', )
    list_display_links = ( 'date', 'username_creation', )
    list_filter = ( 'username', 'date', )
    search_fields = [ 'username', ]

admin.site.register(Log, LogAdmin)

