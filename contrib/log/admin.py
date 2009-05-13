# -*- encoding: utf-8 -*-

from models import Log
from django.contrib import admin

class LogAdmin(admin.ModelAdmin):
    list_display = ( 'date', 'agent', 'username_creation' , 'type', 'details', )
    list_display_links = ( 'date', 'username_creation', )
    list_filter = ( 'username', 'creation', 'date', )
    search_fields = [ 'username', ]

admin.site.register(Log, LogAdmin)

