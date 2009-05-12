# -*- encoding: utf-8 -*-

from models import MailUser

from django.contrib import admin

class MailUserAdmin(admin.ModelAdmin):
    list_display = ( 'mail', 'username' , 'addr_from', 'expire', )
    list_display_links = ( 'mail', 'username', )
    list_filter = ( 'username', )
    search_fields = [ 'username', ]
    fieldsets = [ ( None,
                    { 'fields' : ( 
                            'username',
                            'fullname',
                            ('mail', 'addr_from',), 
                            'expire',
                        )
                    }
                  ),
                  ( 'Données système',
                    {
                      'fields': ( 'maildir', 
                                  'password',
                                ),
                      'classes' : ('collapse',),
                    }
                  ),
                  ( 'Données de gestion',
                    {
                      'fields': ( 'source', ), 
                      'classes' : ('collapse',),
                    }
                  ) ]

admin.site.register(MailUser, MailUserAdmin)

