Les contribs : généralités
==========================

Les contribs sont des applications Django placées dans le répertoire
``/usr/lib/auf-django-users/contrib``.

Il s'agit souvent d'applications qui se greffent sur l'objet ``User`` de
l'application ``nss`` de ``aufusers``, et qui font des opérations spécifiques
lorsqu'un utilisateur NSS est modifié. Par exemple : enregistrer les
modifications, modifier une base de compte de messagerie associée, etc.

Mais puisque les contrib sont des applications Django, on peut imaginer
à l'avenir n'importe quel autre type d'utilisation.

.. Note:: Si vous avez écrit une contrib (ou alors l'idée d'une contrib qui
   vous serait utile), faites-en part à la liste de discussion technique de l'AUF.
   Si elle est utile à plusieurs personnes, elle sera incluse dans les contribs
   fournies automatiquement avec auf-django-users.

Principe technique
------------------

Django envoie un signal lors de la création, la modification ou la suppression
d'un élément. Django propose également un système qui permet d'*accrocher* une
fonction à une signal.

Les contribs de ``auf-django-users`` sont une application de cette possibilité
de Django : on écrit une fonction qui sera executée lors de toute création ou
modification d'un utilisateur. La fonction va recevoir en argument le nouvel
utilisateur : à elle de faire ce qu'elle veut avec...

Les contribs fournies
---------------------

 * ``contrib.log`` : suivi de l'activité sur les comptes NSS. Cette contrib
   est activée par défaut.
 * ``contrib.mail`` : synchronisation des comptes NSS vers une table pour la
   messagerie.
 * ``contrib.log_expire`` : suivi des dates d'expiration des comptes NSS (assez
   peu utile, c'était surtout un test, je la laisse pour l'histoire)

.. Warning:: Ne modifiez pas ces contribs ! Vos modifications seraient perdues à
  la prochaine mise à jour de ``auf-django-users``. Si vous désirez adapter une de
  ces contribs, faites en une copie et activez-la à la place de l'originale.

Des exemples de contrib pour vous inspirer
``````````````````````````````````````````

Quelques exemples sont visibles dans ``/usr/lib/auf-django-users/contrib`` :

 * ``EXEMPLE_sync_mail_base_externe`` : synchronisation avec une base de données *externe* pour la gestion du mail
 * ``EXEMPLE_plugin_user`` : un exemple de connexion sur les objets nss.User


Des idées de contribs à écrire
``````````````````````````````

 * Gestion des données qualitatives (nom, prénoms, genre, naissance, adresses,
   établissement, etc.)
 * Gestion du système VoIP
 * Suivi des commandes de documents primaires
 * Module de comptabilité (émission de reçu, etc)
 * Proposez vos idées !


Comment activer une contrib ?
-----------------------------

Si elle existe, lire la documentation de la contrib : il y aura peut-être des
manipulations particulières à faire. S'il n'y a pas de documentation, essayez
de comprendre le code source Python avant d'activer n'importe quoi... Si vous
êtes perdu, posez la question sur la liste de discussion de l'AUF avant toute
tentative hasardeuse.

Pour une contrib qui n'a pas besoin de configuration ou de table dans une base
de données, la procédure est généralement la suivante :

 #. ajouter le contrib dans le tuple ``INSTALLED_APPS_MORE`` à la fin du fichier ``/etc/auf-django-users/conf.py``
 #. relancer l'application auf-django-users (en général un *restart* de Apache)
 #. normalement, si la contrib est bien programmée, c'est tout !


Description des contribs fournies
---------------------------------

.. toctree::
   :maxdepth: 2

   contrib-log
   contrib-mail

