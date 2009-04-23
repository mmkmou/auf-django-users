# -*- encoding: utf-8 -*-

# Mise en production : hébergement sur un serveur Web en mode WSGI
# Cf http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango

# Pour la configuration apache2 avec module mod_wsgi (libapache2-mod-wsgi)
# voir /etc/auf-django-users/apache.conf

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'aufusers.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

