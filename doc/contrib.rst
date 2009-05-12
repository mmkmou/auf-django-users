Extensions, greffons, *plug-ins* : les contribs
===============================================

.. Warning:: **Cette documentation est en cours d'écriture**

   En attendant, vous pouvez aller voir dans /usr/lib/auf-django-users/contrib
   les exemples de contrib disponibes.

Principe des contribs
---------------------

Lorsqu'une action de type création, modification ou suppression d'un des
éléments Django est effectuée, celui-ci envoie un "signal". Il est ensuite
possible de demander à *accrocher* une fonction à un signal.

Ainsi, on peut écrire une fonction qui sera executée lors de toute création ou
modification d'un utilisateur. La fonction va même recevoir en argument le
nouvel utilisateur, à elle de faire ce qu'elle veut avec...!


Que peut-on faire dans un contrib
---------------------------------

Tout ce qui est programmable en Django et/ou en Python !

Deux contribs classiques
````````````````````````

 * ``contrib.logs`` : suivi de l'activité sur les comptes NSS
 * ``contrib.mail`` : synchronisation des comptes NSS vers une table pour la messagerie

D'autres exemples pour vous inspirer
````````````````````````````````````

Quelques exemples sont visibles dans ``/usr/lib/auf-django-users/contrib`` :

 * ``EXEMPLE_sync_mail_base_externe`` : synchronisation avec une base de données *externe* pour la gestion du mail
 * ``EXEMPLE_plugin_user`` : un exemple de connexion sur les objets nss.User


D'autres idées à développer
```````````````````````````

 * Gestion des données 
 * Gestion du système VoIP
 * ...

Comment activer un contrib ?
----------------------------

Si elle existe, lire la documentation du contrib : il y aura peut-être des
manipulations particulières à faire. S'il n'y a pas de documentation, essayez
de comprendre le code source Python avant d'activer n'importe quoi...

Pour une contrib qui n'a pas besoin de configuration ou de table dans une base
de données, la procédure est généralement la suivante :

 #. ajouter le contrib dans le tuple ``INSTALLED_APPS_MORE`` à la fin du fichier ``/etc/auf-django-users/conf.py``
 #. relancer l'application, c'est-à-dire le serveur qui l'héberge en général
 #. normalement, si la contrib est bien programmée, c'est tout

