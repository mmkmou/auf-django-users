aufusers.contrib.mail
=====================

``contrib.mail`` synchronise les données des comptes NSS vers une table SQL
utilisable par un système de messagerie.

Cette contrib n'est pas activée par défaut. Cela veut dire que la table des
données associée n'est pas créée par défaut. Si vous activez ``contrib.mail``,
vous devez également créer une table ``mail_user``.

.. Warning:: Ne modifiez pas cette contrib ! Vos modifications seraient perdues à
  la prochaine mise à jour de ``auf-django-users``. Si vous désirez adapter cette
  contrib, faites en une copie et activez-la à la place de l'originale.

Table associée à aufusers.contrib.mail
--------------------------------------

Cette contrib a besoin d'une table ``mail_user``. Si elle n'existe pas, il
faudra lancer un ``syncdb`` pour que Django la créé, après que la contrib aura
été activée.

Si vous avez déjà une table ``mail_user``, voici le format qu'elle doit avoir : ::

    CREATE TABLE "mail_users" (
            "username" varchar(128) NOT NULL PRIMARY KEY,
            "password" varchar(64) NOT NULL,
            "expire" integer NOT NULL,
            "fullname" varchar(128) NOT NULL,
            "maildir" varchar(256) NOT NULL,
            "mail" varchar(128) NOT NULL UNIQUE,
            "addr_from" varchar(128) NOT NULL,
            "source" varchar(10) NOT NULL
    );

Activation de aufusers.contrib.mail
-----------------------------------

Pour activer ``aufusers.contrib.mail``, aller dans ``/etc/auf-django-users/conf.py`` et
ajoutez ``'aufusers.contrib.mail'`` dans la liste ``INSTALLED_APPS_MORE``, vers
la fin du fichier.

Si vous n'avez pas de table ``mail_users`` dans la base de données, créez-là avec : ::

 $ auf-django-users-manage.py syncdb

Configuration de aufusers.contrib.mail
--------------------------------------

Cette contrib se configure dans le fichier
``/etc/auf-django-users/contrib.mail.conf.py``. 
Voici le contenu de ce fichier tel que distribué avec ``auf-django-users`` :

.. literalinclude:: ../contrib/mail/conf.py

API de aufusers.contrib.mail.models
-----------------------------------

.. automodule:: aufusers.contrib.mail.models
   :members: MailUser

