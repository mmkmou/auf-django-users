#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# ./list-expire.py <n>
# Affiche la liste des logins des comptes qui expirent dans "n" jours

from aufusers import User

import datetime, sys
date = datetime.date.today() + datetime.timedelta(int(sys.argv[1]))

for user in User.objects.filter(expire=date):
    print u"%s" % user.username

