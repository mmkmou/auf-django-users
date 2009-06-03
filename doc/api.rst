Utilisation du module Python aufusers (API)
===========================================

Le module Python ``aufusers`` propose un certain nombre de sous-modules, de
fonctions et de classes. Ils suivent tous le format d'un projet Django.
Les différents modèles de données, au sens Django, sont donc accessibles
via les classes ``aufusers.<application>.models.<Classe>``.

Ainsi, la classe ``aufusers.nss.models.User`` représente le modèle d'un
utilisateur *nss* du système Unix, modèle au sens Django. On peut donc
effectuer des opérations sur les utilisateurs avec les techniques Django,
par exemple :

 * obtenir un objet utilisateur depuis la base avec ``u=User.objects.get(...)``
 * modifier les données d'un utilisateur avec ``u.gecos='CLEESE John'``
 * obtenir un nouvel utilisateur avec ``u=User(username='john',gecos='CLESSE John')``
 * enregistrer ou modifier un utilisateur dans la base avec ``u.save()``
 * trouver plusieurs utilisateurs dans la base avec ``liste=User.objects.filter(...)``
 * compte le nombre d'utilisateurs total dans la base avec ``n=User.objects.count()``

Cette documentation précise juste les éléments spécifiques par rapport aux
modèles Django classiques. Pour savoir comment les utiliser en détail, il faut
connaître Django. Si vous désirez vous lancer dans cette aventure, commencez
par lire les documents suivants :

 * `le tutoriel Django <http://docs.djangoproject.com/en/1.0//intro/tutorial01/>`_
 * `requêtes en Django <http://docs.djangoproject.com/en/1.0/topics/db/queries>`_
 * `requêtes plus complexes (QuerySet) <http://docs.djangoproject.com/en/1.0/ref/models/querysets/>`_


Ci-dessous la documentation des méthodes spécifiques aux modèles de
``aufusers.nss.models``, qui s'ajoutent ou modifient les méthodes proposées par
défaut par Django.

aufusers.nss.models
-------------------

.. automodule:: aufusers.nss.models
   :members: User, Group, GroupList

Accès direct via aufusers
-------------------------

Pour éclaircir la programmation, le module ``aufusers`` positionne
automatiquement la variable ``DJANGO_SETTINGS_MODULE`` et expose directement
les modèles de ``aufusers.nss``. Ainsi au lieu d'écrire : ::

  # déclarations classiques en mode Django «pur et dur»
  import os
  os.environ['DJANGO_SETTINGS_MODULE']='aufusers.settings'
  from aufusers.nss.models import User, Group, GroupList

  # accès à User, Group ou GroupList
  ...  

on peut juste faire : ::

  from aufusers import User, Group, GroupList

  # accès à User, Group ou GroupList
  ...

Petits exemples d'utilisation
-----------------------------

Modifier le mot de passe de l'utilisateur *test* : ::

  from aufusers import User

  u = User.objects.get(username='test')
  u.password = 'passer'
  u.save()   # le mot de passe sera crypté à ce moment là

Afficher une liste de tous les comptes, avec dates d'expiration et groupes : ::

  from aufusers import User

  for u in User.objects.all():
      print 'Compte %s (%s)' % (u.username, u.gecos)
      print '            expire le : %s' % u.expire
      print '     groupe principal : %s' % u.gid.name
      print '  groupes secondaires : ' + ', '.join([g.name for g in u.secgroups.all()])
      print '-'*40

Compter le nombre d'utilisateurs actifs (date d'expiration dans le futur) : ::

  from aufusers import User
  import datetime

  print "nombre d'utilisateur actifs = %d" % \
        User.objects.filter(expire__gte=datetime.date.today()).count()
        # note : __gte = greater than or equal = plus grand ou egal à 
        # note 2 : avec la puissance de ses QuerySet, sachez que Django ne fait
        # qu'une seule requete SQL pour l'instruction ci dessus... si, si !

Créer 20 utilisateurs formation1,2,3... avec le même mot de passe : ::

  from aufusers import User

  for i in range(1,21):
       User(username="formation%d" % i, password="passer").save()

