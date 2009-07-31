#!/usr/bin/env python

# on veut que tout dans ce script soit executé par l'utilisateur nobody
# dans le groupe auf-d-u
import pwd, grp, os
nobody = pwd.getpwnam('nobody').pw_uid
group = grp.getgrnam('auf-d-u').gr_gid
os.setgid(group)
os.setuid(nobody)

from django.core.management import execute_manager
from aufusers import settings
if __name__ == "__main__":
    execute_manager(settings)

