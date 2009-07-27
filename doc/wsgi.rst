Mise en ligne avec Apache et WSGI
=================================

Pour mettre en ligne le système de façon permanente, la technique conseillée
est d'utiliser un serveur compatible WSGI. ``apache2`` et son module
``libapache2-mod-wsgi`` remplissent parfaitement ce rôle : ::

  # aptitude install apache2 libapache2-mod-wsgi

Un exemple de configuration est disponible dans `/etc/auf-django-users/apache.conf` :

.. literalinclude:: ../apache.conf

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

