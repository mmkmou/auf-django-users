# -*- encoding: utf-8 -*-

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

