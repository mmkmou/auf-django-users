Premiers pas, premiers tests
============================

Configuration par défaut
------------------------

La configuration du système ``auf-django-users`` se fait dans le fichier
``/etc/auf-django-users/conf.py``. Par défaut, la base de donnée est gérée
par SQLite, il s'agit donc d'un simple fichier ``/tmp/base.sqlite3`` : ::

  # extrait du /etc/auf-django-users/conf.py par défaut
  DATABASE_ENGINE = 'sqlite3'
  DATABASE_NAME = '/tmp/base.sqlite3' 

Cette configuration convient parfaitement pour faire un premier test de
l'application.

.. Note::
   Puisque tout va se passer dans ``/tmp``, il n'est pas utile d'être
   administrateur, nous allons lancer le système en tant qu'utilisateur normal de
   la machine.

Initialisation de la base de données de test
--------------------------------------------

Il faut d'abord initialiser la base, en utilisant le script
**auf-django-users-manage.py** avec sa commande ``syncdb``. Notez que lors de
cette initialisation, un compte administrateur va être créé, vous devrez lui
donner un *login* et un mot de passe : ::

  $ auf-django-users-manage.py syncdb
  Creating table auth_permission
  (...)
  Would you like to create one now? (yes/no): yes
  Username (Leave blank to use 'thomas'):
  E-mail address: test@no.way
  Password: 
  Password (again): 
  Superuser created successfully.
  (...)

Une fois cette initialisation effectuée, vous pouvez créer un groupe et un
utilisateurs initiaux pour vos tests. Ces données sont déjà fournies avec
l'application, il vous suffit de les injecter dans la base : ::

  $ auf-django-users-manage.py loaddata group_users
  $ auf-django-users-manage.py loaddata user_test

Lancement du serveur Web de test
--------------------------------

Tout est prêt pour que l'application fonctionne. Nous allons lancer le serveur
Web de test : ::

  $ auf-django-users-manage.py runserver

La partie Web de l'application est alors visible sur http://127.0.0.1:8000/admin/.
Il faut s'y connecter avec le compte administrateur créé lors du ``syncdb``.

Première photo d'écran
----------------------

Pour faire moderne et pour donner envie au lecteur encore hésitant, voici à
quoi ressemble un peu l'application :

.. image:: premiers-pas-connexion.*

Vous accédez alors directement à la liste des utilisateurs disponibles sur le
système :

.. image:: premiers-pas-liste.*

L'interface est sensée être suffisament intuitive pour éviter d'autres explications...

