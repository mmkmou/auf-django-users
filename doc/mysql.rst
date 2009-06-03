Utilisation d'une base MySQL
============================

.. Warning:: **Réglages préliminaires côté MySQL**

   Afin d'éviter les soucis (avec cette application comme avec beaucoup
   d'autre), votre serveur MySQL doit être configuré pour supporter l'encodage
   **utf8** par défaut. Pour cela, voir la page du `wikiteki Etude/Unicode
   <http://wiki.auf.org/wikiteki/Etude/Unicode>`_

Configuration des paramètres de connexion
-----------------------------------------

Les paramètres de connexion à la base doivent être indiqués dans ``/etc/auf-django-users/conf.py`` : ::

  DATABASE_ENGINE = 'mysql"
  DATABASE_NAME = 'auth'
  DATABASE_USER = 'nssadmin'        # utilisateur avec accès SELECT, INSERT, UPDATE et DELETE
  DATABASE_PASSWORD = 'xxx'
  DATABASE_HOST = '219.87.23.11'    # laisser vide si la base est local (localhost)
  DATABASE_PORT = ''                # laisser vide pour le port MySQL par défaut

Si l'application était déjà fonctionnement via un serveur (Apache/WSGI ou
``runserver``), il faut relancer complétement le serveur (avec ``# apache2ctl
restart`` pour Apache, ou en relançant un autre ``runserver``).


Description des tables de la base
---------------------------------

Si vous n'avez pas du tout de base de donnée MySQL pour ``libnss-mysql-bg``,
alors Django les créera pour vous (voir plus loin). Sinon, il faut adapter vos
tables pour qu'elles suivent les schémas ci-dessous.

Tables de l'application nss
```````````````````````````

Rappel: ces schémas ne sont utiles que si vous devez *adapter des tables déjà
existantes*. Si vous n'avez pas encore de base de donnée d'authentification, ne
faites rien : ``auf-django-users`` va les créer pour vous.

**users**
  les utilisateurs, au sens *nss*::

    CREATE TABLE `users` (
        `username` varchar(128) NOT NULL PRIMARY KEY,
        `password` varchar(64) NOT NULL,
        `uid` integer NOT NULL UNIQUE,
        `gid` integer NOT NULL,
        `gecos` varchar(128) NOT NULL,
        `homedir` varchar(256) NOT NULL UNIQUE,
        `shell` varchar(64) NOT NULL,
        `lstchg` integer NOT NULL,
        `min` integer NOT NULL,
        `warn` integer NOT NULL,
        `max` integer NOT NULL,
        `inact` integer NOT NULL,
        `expire` integer NOT NULL,
        `flag` integer NOT NULL,
        `source` varchar(10) NOT NULL,
        `creation` datetime NOT NULL,
        `modification` datetime NOT NULL
    );

  Notes :
   * ``source`` correspondra à la source d'origine des données. Pour les
     données que l'application ``auf-django-users`` gère directement, la source sera
     ``'LOCAL'``. Si une application externe veut pouvoir gérer ses propres données
     dans cette table, elle doit choisir un nom de source différent. C'est le cas
     par exemple si vous avez un script de synchronisation apportant les
     utilisateurs *prenom.nom@auf.org* dans votre base locale.  
   * ``creation`` est la date de création du compte, ``modification`` est la date de dernière
     modification

**groups**
  les groupes d'utilisateurs::

    CREATE TABLE `groups` (
        `name` varchar(32) NOT NULL UNIQUE,
        `password` varchar(64) NOT NULL,
        `gid` integer AUTO_INCREMENT NOT NULL PRIMARY KEY
    );

  et on ajoute une contrainte qui lie les groupes des utilisateurs à ces groupes (une clé distante de ``users.gid`` vers ``groups.gid``). Ceci est facultatif, mais ça peut éviter d'avoir un jour une base de donnée incohérente::

    ALTER TABLE `users` ADD CONSTRAINT gid_refs_gid_60c371b8 FOREIGN KEY (`gid`) REFERENCES `groups` (`gid`);

  Notes :
   * le champ ``password`` est en général fixé à ``'x'``

**grouplist**
  appartenance des utilisateurs à leurs groupes secondaires::

    CREATE TABLE `grouplist` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `gid` integer NOT NULL,
        `username` varchar(128) NOT NULL,
        UNIQUE (`gid`, `username`)
    );

  et on ajoute des contraintes (clés distantes) qui relient les ``username`` à des utilisateurs et les ``gid`` à des groupes. Ce n'est pas indispensable, mais ça peut éviter d'avoir un jour une base de donnée incohérente::

    ALTER TABLE `grouplist` ADD CONSTRAINT gid_refs_gid_6d7c9cff FOREIGN KEY (`gid`) REFERENCES `groups` (`gid`);
    ALTER TABLE `grouplist` ADD CONSTRAINT username_refs_username_5efc4794 FOREIGN KEY (`username`) REFERENCES `users` (`username`);


Tables Django
`````````````

Le système Django va créer ses propres tables afin de gérer les droits des
utilisateurs de l'application, ainsi que tout ce qui concerne la gestion de
l'interface Web. Il n'est pas nécessaire que ses tables existent : Django les
crééra si besoin. 

 * pour l'authentification : ``auth_permission``, ``auth_group``, ``auth_user``, ``auth_message``
 * pour la partie web : ``django_content_type``, ``django_session``, ``django_admin_log``


Création d'une base (à partir de rien)
--------------------------------------

Si vous n'avez pas encore de base MySQL de gestion de vos utilisateurs,
l'application ``auf-django-users-manage.py`` vous permet de la créer facilement : 

 #. Créez une base ``auth`` sur votre serveur MySQL : ::

    > SET character_set_client = utf8;
    > SET NAMES utf8;
    > CREATE DATABASE auth DEFAULT CHARACTER SET utf8;

 #. Créez 4 utilisateurs associés à cette base :

    - ``nsscreate`` : tous les droits sur la base
    - ``nssadmin`` : droits SELECT, INSERT, UPDATE et DELETE
    - ``nssread`` : droits SELECT partout *sauf sur les champs password*
    - ``nssreads`` : droits SELECT partout

    .. TODO ajouter les commandes correspondantes

 #. Dans ``/etc/auf-django-users/conf.py``, indiquez l'utilisateur ``nsscreate`` (celui qui a tous les droits sur la base)

 #. Lancer la création des tables : ::
    
    $ auf-django-users-manage.py syncdb

 #. Vous pouvez alors ajouter un utilisateur et un groupe initial dans la base : ::

    $ auf-django-users-manage.py loaddata utilisateur_test

 #. Dans ``/etc/auf-django-users/conf.py``, changez l'utilisateur pour
    ``nssadmin`` (qui n'a pas les droits de modification de la structure des
    tables)

 #. Si votre application est hébergée en WSGI sur Apache, n'oubliez pas de
    relancer ce dernier : ::

    # apache2ctl restart


Utilisation d'une base déjà existante
-------------------------------------

 #. Adaptatez vos tables (notamment avec ``ALTER TABLE``) afin de les rendre conformes aux modèles indiqués ci-dessus

 #. Lancer ``$ auf-django-users-manage.py syncdb`` pour ajouter les tables manquantes (notamment celles de Django)

.. Note:: **si la base de donnée MySQL n'était pas en utf8**, il faut absolument
   convertir les tables Django **juste après le syncdb** : ::

     ALTER TABLE auth_permission CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
     ALTER TABLE auth_group CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
     ALTER TABLE auth_user CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
     ALTER TABLE auth_message CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
     ALTER TABLE django_content_type CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
     ALTER TABLE django_session CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
     ALTER TABLE django_admin_log CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;

