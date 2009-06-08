Mise en ligne avec Apache et WSGI
=================================

Pour mettre en ligne le système de façon permanente, la technique conseillée
est d'utiliser un serveur compatible WSGI. ``apache2`` et son module
``libapache2-mod-wsgi`` remplissent parfaitement ce rôle : ::

  # aptitude install apache2 libapache2-mod-wsgi

Un exemple de configuration est disponible dans `/etc/auf-django-users/apache.conf` : ::

  # à placer dans un <VirtualHost ...>
  WSGIScriptAlias / /usr/share/auf-django-users/aufusers.wsgi
  Alias /media /usr/share/auf-django-users/media
  <Directory /usr/share/auf-django-users/media>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride None
    Order allow,deny
    allow from all
  </Directory>
  # partie statique de l'admin : celle fournie par Django
  Alias /admin/media /usr/share/python-support/python-django/django/contrib/admin/media
  <Directory /usr/share/python-support/python-django/django/contrib/admin/media/>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride None
    Order allow,deny
    allow from all
  </Directory>

.. note::
   Si la base de donnée est en SQLite (c'est le cas en mode *test*), il faut que l'utilisateur
   du serveur Web ``apache2`` ait les droits en lecture et écriture sur le fichier sqlite
   de la base de données. Pour cela, sous Debian/Ubuntu il suffit de faire : ::

        $ chgrp www-data /tmp/base.sqlite3
        $ chmod g+rw /tmp/base.sqlite3


En cas de modification de l'application
---------------------------------------

Si vous modifiez l'application, **y compris sa configuration**, vous devez relancer complétement le serveur Apache : ::
  
  # apache2ctl restart

Notez qu'un simple *graceful* ne suffit pas. Il faut absolument un *restart*.

