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

# UID minimale
MIN_UID = 10000

# GID par défaut
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
# Gestion de la messagerie
#

# domaine par défaut des comptes de messagerie
DOMAINE = "refer.sn"

# adresse mail par défaut. si cette adresse n'est pas changée dans les
# formulaires, alors les champs mail et addr_from seront automatiquement
# calculés (par des méthode redéfinissables, cf plus bas)
MAIL = "prenom.nom@" + DOMAINE

# Valeur du "maildir" par défaut dans le formulaire. Si cette valeur n'est pas
# modifiée lors de la création d'un utilisateur, alors son maildir sera calculé
# par la formule suivante : MAILDIR_BASE + '/' + username
MAILDIR_BASE = "/var/mail/" + DOMAINE

# Il est possible de personnaliser le calcul automatique des variables
# mail, addr_from ou maildir en déclarant des fonctions. Exemples :
#def mail(user):
#    """renvoie un mail (format user@domaine)"""
#    return "%s@%s" % (user.username, DOMAINE)
#def addr_drom(user):
#    """renvoie un mail (format user@domaine)"""
#    return "%s@%s" % (user.username, DOMAINE)
#def maildir(user):
#    """renvoie un répertoire Maildir"""
#    return "/var/mail/%s" % user.username

# Synchro de nss vers mail. Valeurs possibles dans la liste:
#  'create' = creation/suppression d'un utilisateur
#  'password' = modification du mot de passe
#  'expire' = modification de la date d'expiration
#  'fullname' = le nom complet (gecos)
#  'all' = toutes ces modifications 
sync_nss2mail = ( 'all' )



#
# Plugins locaux dans /usr/lib/auf-django-users/contrib
# Exemple :
# INSTALLED_APPS_MORE = (
#   'aufusers.contrib.sync_mail_base_externe',
# )
INSTALLED_APPS_MORE = ()

