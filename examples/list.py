#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# on importe les classes dont on a besoin (parmis User, Group, GroupList, ...)
from aufusers import User

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

