# -*- encoding: utf-8 -*-

from models import LogExpire

from django.contrib import admin

class LogExpireAdmin(admin.ModelAdmin):
    list_display = ( 'modification', 'username_creation' , 'expire', 'total_jours', )
    list_display_links = ( 'modification', 'username_creation', )
    list_filter = ( 'username', 'creation', 'modification', )
    search_fields = [ 'username', ]
    fieldsets = [ ( None,
                    { 'fields' :
                        ( ( 'username', 'creation' ),
                          ( 'expire', 'modification'),
                          'total_jours'
                        )
                    }
                ) ]

admin.site.register(LogExpire, LogExpireAdmin)

