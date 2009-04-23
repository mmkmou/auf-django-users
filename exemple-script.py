#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# on indique quel sera le module de configuration
import os
os.environ['DJANGO_SETTINGS_MODULE']="aufusers.settings"

# et on importe les classes du modèle de l'application "nss"
# (User, Group, GroupList)
from aufusers.nss.models import *

# A partir de là commence le script en tant que tel, utilisant les
# classes et leurs méthodes... Ici on va faire la liste de tous les
# comptes et pour chacun préciser sa date d'expiration.

for user in User.objects.all():   # parcours la liste des abonnés
    print u"compte '%s' (%s)" % (user.username, user.gecos)
    if user.active():
        print u"         \_ expirera le %s" % user.expire
    else:
        print u"         \_ a expiré le %s" % user.expire
    print " "

