# -*- encoding: utf-8 -*-

#
# Exemple de plugin local pour aufusers
#

# pour connexion avec le module de gestion des comptes NSS
from django.db.models.signals import post_save, post_delete
from aufusers import User

def user_post_save(sender, **kwargs):
    """procédure lancée après chaque création ou modification d'un User"""
    user = kwargs['instance']
    # faire ici le traitement ...

# connexion au signal "abonné enregistré"
post_save.connect(user_post_save, sender=User)

def user_post_delete(sender, **kwargs):
    """procédure lancée après chaque destruction d'un User"""
    user = kwargs['instance']
    # faire ici le traitement ...

# connexion au signal "abonné détruit"
post_delete.connect(user_post_delete, sender=User)

