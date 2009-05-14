# -*- encoding: utf-8 -*-

from models import Log
from django.contrib import admin

class LogAdmin(admin.ModelAdmin):
    list_display = ( 'username_creation', 'colored_modif', 'date', 'agent')
    ordering = ( '-date', )
    list_display_links = ( 'date', )
    list_filter = ( 'username', 'date', )
    search_fields = [ 'username', ]

admin.site.register(Log, LogAdmin)

