# -*- encoding: utf-8 -*-
"""
Pour chaque abonné (compte *nss*), trace l'historique des modifications.
"""

from django.db import models

import datetime

# pour connexion avec le module de gestion des comptes nss
from django.db.models.signals import pre_save, post_save, post_delete
from aufusers.nss.models import User

# pour comparer les mots de passe...
from aufusers.lib.utils import password_crypt


MODIFICATION_TYPES = (
    ('create','Création du compte'),
    ('delete','Suppression du compte'),
    ('password','Modification du mot de passe'),
    ('expire','Modification de la date d\'expiration'),
    ('gecos','Modification des informations GECOS'),
    ('other','Autre modification'),
)

# style de l'affichage des type de modifs dans l'admin
MODIFICATION_STYLES = {
    'create': 'color: green;',
    'delete': 'color: red; text-decoration: line-through;',
    'password': 'color: red;',
    'expire': 'color: blue;',
    'gecos': 'color: black;',
    'other': 'color: black;',
}

class Log(models.Model):
    """
    Un *Log* représente une modification d'un certain utilisateur à un certain moment.

     * ``username`` et ``creation`` : nom d'utilisateur et sa date de création,
       qui permettent de retrouver de quel utilisateur il s'agit. On doit
       fournir la date de création, car l'utilisateur 'toto' créé en 2009
       est différent de l'utilisateur 'toto' créé en 2004 puis supprimé en 2006.
     * ``type`` et ``details`` : type de la modification, et détails annexes éventuels
     * ``date`` : date de la modification
     * ``agent`` : personne ayant demandé la modification

    """
    username = models.CharField("nom d'utilisateur", max_length=64)
    creation = models.DateTimeField("date de création du compte")
    type = models.CharField("type de la modification", max_length="16",
        choices=MODIFICATION_TYPES, default='other', blank=False)
    details = models.CharField("détails", max_length=128, default='')
    date = models.DateTimeField("date de la modification", auto_now_add=True)
    agent = models.CharField("modificateur", max_length=32)

    class Meta:
        db_table = "log"
        verbose_name = "suivi d'un compte"
        verbose_name_plural = "suivis des comptes"

    def __unicode__(self):
        return u"%s : modification %s le %s par %s" % \
            (self.username, self.type, self.date, self.agent)

    def username_creation(self):
        """Affichage de la clé d'un utilisateur = username + date de création"""
        return u"%s (crée le %s)" % (self.username, self.creation.date())
    username_creation.short_description = 'utilisateur'
    username_creation.admin_order_field = 'username'

    def colored_type(self):
        """Affichage du type de modification, en couleur et en odorama"""
        return u'<span style="%s">%s</span>' % (MODIFICATION_STYLES[self.type], self.get_type_display())
    colored_type.short_description = "Type de la modification"
    colored_type.allow_tags = True
    colored_type.admin_order_field = 'type'

    def save(self, force_insert=False, force_update=False):
        """
        Enregistre une nouvelle modification pour un compte.
        Particularités : on interdit la possibilité de modifier un log
        """
        return super(Log, self).save(force_insert=True, force_update=False)

    def delete(self):
        """
        Cette methode ne fait *rien* car on interdit le delete dans les logs.

        Attention : cette méthode n'est appelée que pour un objet donné (donc
        notamment dans l'interface d'admin). Un QuerySet.delete() n'appelle pas
        cette fonction. Il reste donc facile d'effacer une ligne de log
        quand on passe directement par la programmation Python.
        """
        return

# 
# fonctions qui vont écouter l'activité sur les autres éléments
# et agir en fonction
#

# détection des modifications (lors du pre_save)
def user_pre_save(sender, **kwargs):
    """Procédure lancée avant chaque modification d'un abonné. On compare
    les données avec l'utilisateur actuel, et on conserve dans un attribut
    log_post_save toutes les modifications constatées. Ces modifications seront
    logées lors du post_save, donc quand le save() aura vraiment fonctionné."""
    user = kwargs['instance']
    # on ne comptabilise que les comptes locaux
    if user.source != 'LOCAL':
        return
    # agent = la personne qui a fait la modification. Si la modification a été
    # faite par le formulaire web, on aura un attribut 'user.agent', sinon on
    # prend la valeur '<api>'
    try:
        agent = user.agent.username
    except:
        agent = '<api>'
    # on cherche les données actuelles de l'utilisateur
    try:
        current = User.objects.get(username=user.username, creation=user.creation)
    except User.DoesNotExist:
        # Si l'utilisateur n'existe pas encore, comme on est dans le pre_save 
        # c'est qu'il s'agit d'une création : le log se fera load du post_save,
        # car c'est lors du post_save qu'on aura la donnée user.creation
        return
    # on stocke chaque modification détectée dans un dictionnaire log_post_save
    # que l'on ajoute comme attribut à user
    user.log_post_save={}
    if password_crypt( user.password ) != current.password:
        user.log_post_save['password'] = ''
    if user.expire != current.expire:
        user.log_post_save['expire'] = "%s -> %s (%+d)" % (current.expire, user.expire, (user.expire-current.expire).days)
    if user.gecos != current.gecos:
        user.log_post_save['gecos'] = "'%s' -> '%s'" % (current.gecos, user.gecos)

# connexion au signal "abonné enregistré"
pre_save.connect(user_pre_save, sender=User)


# log des créations/modifications des comptes (post_save)
def user_post_save(sender, **kwargs):
    """Procédure lancée après l'ajout ou la modification d'un abonné.
    S'il s'agit d'une création alors on log la création, sinon on log les
    modifications détectées lors du pre_save."""
    user = kwargs['instance']
    # on ne log que pour les comptes locaux
    if user.source == 'LOCAL':
        # agent = la personne qui a fait la modification. Si la modification a été
        # faite par le formulaire web, on aura un attribut 'user.agent', sinon on
        # prend la valeur '<api>'
        try:
            agent = user.agent.username
        except:
            agent = '<api>'
        if kwargs['created'] :
            # il s'agit d'une création
            details = "uid %s, nom complet '%s'" % (user.uid, user.gecos)
            Log( username = user.username, creation = user.creation,
                 type = 'create', agent = agent , details = details ).save()
        else:
            # c'est une modification : on enregistre ce qui avait été
            # détecté lors du pre_save
            for type in getattr(user,'log_post_save',()):
                Log( username = user.username, creation = user.creation,
                     type = type, details = user.log_post_save[type],
                     agent = agent ).save()

# connexion au signal "abonné enregistré"
post_save.connect(user_post_save, sender=User)


# log de la suppression des comptes (post_delete)
def user_post_delete(sender, **kwargs):
    """Procédure lancée après chaque suppression d'un abonné.

    ATTENTION : cette methode n'est pas appelé lors d'un QuerySet.delete()
    sur des objets User. Il faut donc TOUJOURS supprimer les User un par un."""
    user = kwargs['instance']
    # on ne comptabilise que les comptes locaux
    if user.source != 'LOCAL':
        return
    # agent = la personne qui a fait la modification. Si la modification a été
    # faite par le formulaire web, on aura un attribut 'user.agent', sinon on
    # prend la valeur '<api>'
    # FIXME : ça ne marchera pas pour le delete
    #         cf http://code.djangoproject.com/ticket/11108
    try:
        agent = user.agent.username
    except:
        agent = '<api>'
    Log( username = user.username,
         creation = user.creation,
         type = 'delete',
         agent = agent ).save()

# connexion au signal "abonné supprimé"
# RAPPEL : ce signal est lancé uniquement lorsqu'on efface un objet ; il n'est
# pas lancé lors d'un QuerySet.delete() !
post_delete.connect(user_post_delete, sender=User)

