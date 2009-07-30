# -*- encoding: utf-8 -*-

__version__ = '0.5.14'
__authors__ = [ 'Thomas NOEL <thomas.noel@auf.org>', ]

import os
os.environ['DJANGO_SETTINGS_MODULE'] = "aufusers.settings"

# On importe directement User, Group et GroupList au niveau de aufusers
# afin de permettre l'import suivant : "from aufusers import User"
from aufusers.nss.models import User, Group, GroupList
