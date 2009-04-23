# -*- encoding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # documentation admin ('django.contrib.admindocs' in INSTALLED_APPS):
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # interface d'administration
    (r'^admin/(.*)', admin.site.root),
    # exemple de template
    (r'^nss/', include('aufusers.nss.urls')),
    # redirection de / vers la gestion des utilisateurs nss
    ('^/*$', 'django.views.generic.simple.redirect_to', {'url': 'admin/nss/user/'}),
)

# cf http://docs.djangoproject.com/en/1.0/howto/static-files/
if settings.DEBUG:
    urlpatterns = patterns('',
        # /media est envoyée par l'application (en production,
        # c'est une partie statique à renvoyer directement via apache ou autre)
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
        # documentation sphinx (statique)
        (r'^auf-django-users-doc/(?P<path>.*)$', 'django.views.static.serve',
            { 'document_root': '/usr/share/doc/auf-django-users/html/',
              'show_indexes': True }),
    ) + urlpatterns

