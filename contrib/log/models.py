# -*- encoding: utf-8 -*-
"""
Pour chaque abonné (compte *nss*), trace l'historique des modifications.
"""

from django.db import models

# pour connexion avec le module de gestion des comptes nss
from django.db.models.signals import pre_save, post_save, post_delete
from aufusers.nss.models import User

# pour comparer les mots de passe...
from aufusers.lib.utils import password_crypt

# pour stocker les détails : json
try:
    import json
except:
    import simplejson as json

import datetime, time, re


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
     * ``type`` et ``details`` : type de modification, et détails annexes
       éventuels (en format json)
     * ``date`` : date de modification
     * ``agent`` : personne ayant demandé la modification

    """
    username = models.CharField("nom d'utilisateur", max_length=64)
    creation = models.DateTimeField("date de création du compte")
    type = models.CharField("type de modification", max_length="16",
        choices=MODIFICATION_TYPES, default='other', blank=False)
    details = models.CharField("détails (format json)", max_length=128, default='')
    date = models.DateTimeField("date de modification", auto_now_add=True)
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

    INFINITY = datetime.date(2038, 01, 19)

    @property
    def details_dict(self):
        """
        Interprete les données JSON du champ details, renvoie un dictionnaire.
        Transforme les dates (expire) en objets datetime.date. 
        NB : si "details" n'est pas au format JSON, tente d'analyser les
        données depuis l'ancien format de log (string). On gère l'historique, quoi.
        """
        try:
            dic = json.loads(self.details)
            # tous les champs nommés 'expire*' sont des dates, on les
            # transforme en objets datetime.date
            for key in dic:
                if key.startswith('expire'):
                    dic[key] = datetime.date(*time.strptime(dic[key],'%Y-%m-%d')[:3])
            return dic
        except:
            # ce n'est pas du JSON, alors c'est un log dans l'ancien format (version < 0.5.10)
            # on analyse alors la chaine de caractère... gestion de l'historique très bêbete,
            # mais ça marche.
            if self.type == 'create':
                r = re.match("^uid (?P<uid>\d+), nom complet '(?P<gecos>.*)'", self.details)
                if r:
                    dic = r.groupdict()
                    dic['uid'] = int(dic['uid'])
                    dic['expire'] = self.INFINITY # l'ancien système de log ne logait pas l'expire :(
                    return dic
                else:
                    return { 'uid': 0, 'gecos': '(inconnu)', 'expire': self.INFINITY }
            elif self.type == 'gecos':
                r = re.match("^'(?P<gecos_old>.*)' -> '(?P<gecos_new>.*)'", self.details)
                if r:
                    return r.groupdict()
                else:
                    return { 'gecos_old': '(inconnu)', 'gecos_new': '(inconnu)' }
            elif self.type == 'expire':
                r = re.match("^(?P<expire_old>\d{4}-\d{2}-\d{2}) -> (?P<expire_new>\d{4}-\d{2}-\d{2})", self.details)
                if r:
                    dic = r.groupdict()
                    for key in dic:  # on transforme les expire* en objets datetime.date
                        dic[key] = datetime.date(*time.strptime(dic[key],'%Y-%m-%d')[:3])
                    return dic
                else:
                    return { 'expire_old': self.INFINITY, 'expire_new': self.INFINITY }
            elif self.type == 'delete':
                return { 'expire' : self.INFINITY } # l'ancien système de log ne logait pas l'expire :(
            else: # autres cas : on ne loggue rien
                return { }
                
    @property
    def details_str(self):
        return ', '.join([ '%s=%s' % (key, value) for key,value in self.details_dict.items() ])

    def colored_modif(self):
        """Affichage de la modification, en couleur et en odorama"""
        if self.details:
            modif = "%s : %s" % (self.get_type_display(), self.details_str)
        else:
            modif = self.get_type_display()
        return u'<span style="%s">%s</span>' % (MODIFICATION_STYLES[self.type], modif)
    colored_modif.short_description = "Modification"
    colored_modif.allow_tags = True
    colored_modif.admin_order_field = 'type'

    def colored_type(self):
        """Affiche du type de modif, en couleur"""
        return u'<span style="%s">%s</span>' % (MODIFICATION_STYLES[self.type], self.type)
    colored_type.short_description = "Type"
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

def json_serial(obj):
    """
    Fonction qui serialise un objet python. Utilisée pour JSONifier
    des dictionnaires contenant des objets datetime.date, qui seront
    enregistrés en string de forme YYYY-MM-DD.
    """
    return '%s' % obj


def user_pre_save(sender, **kwargs):
    """
    Procédure de détection des modifications, lancée avant modification d'un abonné.
    On compare les données avec l'utilisateur actuel, et on conserve dans un
    attribut log_post_save toutes les modifications constatées. Ces
    modifications seront logées lors du post_save, donc quand le save() aura
    vraiment fonctionné.
    """
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
        user.log_post_save['expire'] = json.dumps({ 'expire_old': current.expire,
                                                    'expire_new': user.expire }, default=json_serial)
    if user.gecos != current.gecos:
        user.log_post_save['gecos'] = json.dumps({ 'gecos_old': current.gecos,
                                                   'gecos_new': user.gecos}, default=json_serial)

# connexion au signal "abonné enregistré"
pre_save.connect(user_pre_save, sender=User)


def user_post_save(sender, **kwargs):
    """
    Procédure d'enregistrement des crétions et modifications, lancée après
    l'ajout ou la modification d'un abonné. S'il s'agit d'une création alors
    on log la création, sinon on log les modifications détectées lors du
    pre_save.
    """
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
            details = json.dumps({ 'uid' : user.uid,
                                   'gecos': user.gecos,
                                   'expire': user.expire }, default=json_serial)
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


def user_post_delete(sender, **kwargs):
    """
    Procédure qui enregistre la suppression d'un abonné.
    ATTENTION : cette methode n'est pas appelé lors d'un QuerySet.delete()
    sur des objets User. Il faut donc TOUJOURS supprimer les User un par un.
    """
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
         agent = agent,
         details = json.dumps({ 'expire': user.expire }, default=json_serial) ).save()

# connexion au signal "abonné supprimé"
# RAPPEL : ce signal est lancé uniquement lorsqu'on efface un objet ; il n'est
# pas lancé lors d'un QuerySet.delete() !
post_delete.connect(user_post_delete, sender=User)

