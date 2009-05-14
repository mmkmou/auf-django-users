aufusers.contrib.log
=====================

``contrib.log`` conserve une trace des modifications effectuées sur les comptes NSS
dans une table ``log``.

Cette contrib est activée par défaut. Cela veut dire que la table ``log`` des
données associée est créée par défaut.

.. Warning:: Ne modifiez pas cette contrib ! Vos modifications seraient perdues à
  la prochaine mise à jour de ``auf-django-users``. Si vous désirez adapter cette
  contrib, faites en une copie et activez-la à la place de l'originale.

Table associée à aufusers.contrib.log
-------------------------------------

Cette contrib utilise une table ``log`` dont voici le schéma : ::

    CREATE TABLE "log" (
            "id" integer NOT NULL PRIMARY KEY,
            "username" varchar(64) NOT NULL,
            "creation" datetime NOT NULL
            "type" varchar(16) NOT NULL,
            "details" varchar(32) NOT NULL,
            "date" datetime NOT NULL,
            "agent" varchar(32) NOT NULL
    );


Activation de aufusers.contrib.log
----------------------------------

Rappel: ``aufusers.contrib.log`` est activée par défaut. La procédure qui suit n'est
utile que si vous devez ré-activer cette contrib.

Pour activer ``aufusers.contrib.log``, aller dans ``/etc/auf-django-users/conf.py`` et
ajoutez ``'aufusers.contrib.log'`` dans la liste ``INSTALLED_APPS_MORE``, vers
la fin du fichier.

Si vous n'avez pas déjà une table ``log`` dans la base de données, créez-la avec : ::

 $ auf-django-users-manage.py syncdb

Configuration de aufusers.contrib.log
-------------------------------------

Il n'y a pas de configuration pour cette contrib.


API de aufusers.contrib.log.models
----------------------------------

.. automodule:: aufusers.contrib.log.models
   :members: Log

