Utilisation du module Python aufusers (API)
===========================================

.. Warning:: cette API n'est pas super stable. On attendra la version 1.0 prévue
   pour février 2013.

Le module Python ``aufusers`` propose un certain nombre de sous-modules, de
fonctions et de classes. Ils suivent tous le format d'un projet Django.
Les différents modèles de données, au sens Django, sont donc accessibles
via les classes ``aufusers.<application>.models.<Classe>``.

Ainsi, la classe ``aufusers.nss.models.User`` représente le modèle d'un
utilisateur *nss* du système Unix, modèle au sens Django. On peut donc
effectuer des opérations sur un utilisateur avec les techniques Django.

Cette documentation précise juste les éléments spécifiques par rapport aux
modèles Django classiques. Pour savoir comment les utiliser, il faut connaître
Django.  Pour cela, vous pouvez commencer par lire les documents suivants :

 * `le tutoriel Django <http://docs.djangoproject.com/en/1.0//intro/tutorial01/>`_
 * `requêtes en Django <http://docs.djangoproject.com/en/1.0/topics/db/queries>`_
 * `requêtes plus complexes (QuerySet) <http://docs.djangoproject.com/en/1.0/ref/models/querysets/>`_

Petit exemple d'utilisation : ::

  import os
  os.environ['DJANGO_SETTINGS_MODULE']="aufusers.settings"
  from aufusers.nss.models import User

  u = User.objects.get(username='test')
  u.password = 'passer'
  u.save()   # le mot de passe sera bien crypté

  for u in User.objects.all():
      print '%s = %s' % (u.username, u.gecos)
      print '  appartient au groupe ' % (u.gid.name)
      print '  et aux groupes ' + ', '.join([g.name for g in u.groups.all()])

.. TODO ajouter d'autres exemples... bof... ipython, les mecs...

aufusers.nss.models
-------------------

.. automodule:: aufusers.nss.models
   :members: User, Group, GroupList

Accès direct via aufusers
-------------------------

Pour eclaircir la programmation, le module ``aufusers`` positionne
automatiquement la variable ``DJANGO_SETTINGS_MODULE``. et expose directement
quelques modèles de ``aufusers``. Ainsi au lieu d'écrire : ::

  import os
  os.environ['DJANGO_SETTINGS_MODULE']="aufusers.settings"
  from aufusers.nss.models import User, Group, GroupList

  # accès à des objets User, Group ou GroupList

on peut juste faire : ::

  from aufusers import User, Group, GroupList

  # accès à des objets User, Group ou GroupList


API de contribs classiques
--------------------------

contrib.log
```````````

Il s'agit d'une contrib que tout le monde activera sans doute. D'ailleurs, elle est activée par défaut.

.. automodule:: aufusers.contrib.log.models
   :members: Log

contrib.mail
````````````

.. automodule:: aufusers.contrib.mail.models
   :members: MailUser

