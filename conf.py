# -*- encoding: utf-8 -*-

#
# Base de données à utiliser
#

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' ou 'oracle'.
DATABASE_NAME = '/tmp/base.sqlite3'    # si sqlite3, c'est le nom du fichier
DATABASE_USER = ''             # inutile en sqlite3.
DATABASE_PASSWORD = ''         # inutile en sqlite3.
DATABASE_HOST = ''             # vide pour localhost. Inutile en sqlite3.
DATABASE_PORT = ''             # vide pour le port par défaut. Inutile en sqlite3.

# Activation/désactivation du mode debug (application et système de template)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

#
# Gestion des utilisateurs
#

# Shells de connexion acceptés
# Le premier est la valeur par défaut
SHELLS = (
    ('/bin/false', 'Désactivé (/bin/false)'),
    ('/bin/sh', 'Par défaut (/bin/sh)'),
    ('/bin/bash', 'Bourne-Again Shell'),
    ('/bin/csh', 'C Shell'),
)

# Valeur du "home" par défaut dans le formulaire. Si cette valeur n'est pas
# modifiée lors de la création d'un utilisateur, alors son homedir sera calculé
# par la formule suivante : HOMEBASE + '/' + username
HOME_BASE = "/home"

# UID minimal pour un utilisateur
MIN_UID = 10000

# GID minimal pour un groupe
MIN_GID = 10000

# GID par défaut pour un utilisateur ("users")
DEFAULT_GID = 100

# Pour proposer son propre calcul du homedir, il suffit de créer une fonction
# homedir() qui prend en argument un utilisateur et renvoie la chaine
# de caractère correspondant au homedir. Exemple :
#
#def homedir(user):
#    """renvoie un homedir au format /home/t/thomas"""
#    return "%s/%s/%s" % (HOME_BASE, user.username[0], user.username)
#
# On peut aussi proposer un date d'expiration par défaut :
#
#import datetime
#def default_expire():
#    """renvoie la date actuelle..."""
#    return datetime.date.today()


#
# Activation des contribs (plug-ins situés dans /usr/lib/auf-django-users/contrib)
#
INSTALLED_APPS_MORE = (
    'aufusers.contrib.log',
    # 'aufusers.contrib.log_expire',
    # 'aufusers.contrib.mail',
)


# note : la configuration de contrib.mail se fait dans le fichier
# /etc/auf-django-users/contrib.mail.conf.py

