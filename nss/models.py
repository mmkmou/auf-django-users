# -*- encoding: utf-8 -*-
"""

Les classes **User**, **Group** et **GroupList** définies dans ce modèle sont
une représentation des tables ``users``, ``groups`` et ``grouplist`` d'une base
de données suivant le format de ``libnss-mysql-bg``.

Il s'agit de la représentation classique des utilisateurs et groupes sous Unix
pour le système **nss** (Name Service Switch).

"""

from django.db import models
from aufusers.lib.expire import ExpireField
from aufusers.lib.utils import password_crypt
import datetime


# configurations par défault (peuvent être redéfinies dans le conf.py)

# Shells de connexion acceptés , le premier est la valeur par défaut
SHELLS = (
    ('/bin/false', 'Désactivé (/bin/false)'),
    ('/bin/sh', 'Par défaut (/bin/sh)'),
)

# Valeur du "home" par défaut dans le formulaire. Si cette valeur n'est pas
# modifiée lors de la création d'un utilisateur, alors son homedir sera calculé
# par la formule suivante : HOMEBASE + '/' + username
HOME_BASE = "/home"

# Renvoie le homedir d'un utilisateur
def homedir(user):
    return "%s/%s" % (HOME_BASE, user.username)

# UID minimal pour un utilisateur
MIN_UID = 10000
# GID minimal pour un groupe
MIN_GID = 10000
# GID par défaut pour un utilisateur ("users")
DEFAULT_GID = 100

# Renvoie la date d'expiration par défaut
def default_expire(): 
    # retourne la date de fin du mois actuel (j'ai pas mieux comme algo, j'ai
    # peu de neurone) : on se place au debut du mois actuel, on va 32 plus
    # tard, on prend le premier jour du mois obtenu... et on recule d'un jour.
    # Ouf.
    return ( datetime.date.today().replace(day=1) + \
             datetime.timedelta(32) ).replace(day=1) - datetime.timedelta(1)

# import de la configuration : on peut y écraser toutes les définitions
# précédentes
from aufusers.conf import *


class User(models.Model):
    """
        Représentation d'un utilisateur au sens Unix (nss). Voici les champs disponibles :

         * ``username`` : nom de l'utilisateur, uniquement composé de lettres minuscules et de chiffres. C'est la *clé primaire*
         * ``password`` : mot de passe de l'utilisateur, crypté
         * ``uid`` : numéro identifiant l'utilisateur
         * ``gid`` : objet Group auquel appartient l'utilisateur
         * ``secgroups`` : liste des groupes secondaires auquel appartient l'utilisateur (c'est un *ManyRelatedManager*)
         * ``gecos`` : nom et prénom, sous la forme Prenom NOM (sans aucun accent)
         * ``homedir`` : répertoire personnel ($HOME)
         * ``shell`` : interpréteur de commande
         * ``lstchg`` : date du dernier changement du mot de passe (*datetime.date*)
         * ``min`` : nombre de jours à attendre avant de pouvoir changer le mot de passe
         * ``warn`` : nombre de jours d'avertissement avant la fin mot de passe
         * ``max`` : nombre de jours après lesquels le mot de passe doit être changé
         * ``inact`` : nombre de jours après la fin de validité provoquant la désactivation du compte
         * ``expire`` : date d'expiration du compte. Il s'agit d'un objet *datetime.date*
         * ``flag`` : champ réservé
         * ``source`` : source des données de cet utilisateur (== 'LOCAL' si l'utilisateur est géré par l'application)
         * ``creation`` : date de création de l'utilisateur dans la base de donnée
         * ``modification`` : date de la dernière modification des données de l'utilisateur

    """

    username = models.CharField("nom d'utilisateur", max_length=128, primary_key=True,
            help_text="Indiquez un identifiant de connexion, uniquement composé de lettres minuscules et de chiffres")
    password = models.CharField("mot de passe (crypté)", max_length=64, default='x')
    uid = models.IntegerField("userID", unique=True) 
    gid = models.ForeignKey("Group", db_column= "gid", default=DEFAULT_GID,
            help_text="Ne modifiez que si vous savez exactement ce que vous faîtes !")
    secgroups = models.ManyToManyField("Group", related_name='groups', through='GroupList', blank=True)
    gecos = models.CharField("informations GECOS", max_length=128, blank=True,
            help_text="Indiquez le nom et le prénom, sous la forme Prenom NOM (sans aucun accent)")
    homedir = models.CharField("répertoire personnel (home)", max_length=256,
            default=HOME_BASE, unique=True,
            help_text="Laissez à <em>" + HOME_BASE + "</em> et la valeur sera calculée automatiquement")
    shell = models.CharField("interpréteur de commande (shell)", max_length=64, 
            choices=SHELLS, default=SHELLS[0][0], blank=False)
    # informations shadow (pour expire ; les autres ne sont pas utilisées pour l'instant)
    lstchg = ExpireField("dernier changement du mot de passe", default = 1,
            help_text="date du dernier changement de mot de passe")
    min = models.IntegerField("durée minimale du mot de passe", default = 0,
            help_text="nombre de jours à attendre avant de pouvoir changer le mot de passe")
    warn = models.IntegerField("durée d'avertissement", default = 0, 
            help_text="nombre de jours d'avertissement avant la fin mot de passe")
    max = models.IntegerField("durée maximale du mot de passe", default = 99999,
            help_text="nombre de jours après lesquels le mot de passe doit être changé")
    inact = models.IntegerField("", default = 0,
            help_text="nombre de jours après la fin de validité provoquant la désactivation du compte")
    expire = ExpireField("date d'expiration", default=default_expire)
    flag = models.IntegerField("réservé", default = 0)
    # champs spécifiques "auf" : source de provenance des données et dates automatiques
    source = models.CharField("source", max_length=10, default="LOCAL")
    creation = models.DateTimeField("date de création", auto_now_add=True)
    modification = models.DateTimeField("dernière modification", auto_now=True)

    def __unicode__(self):
        """Représentation d'un utilisateur : son login suivi de son uid"""
        return "%s (%s)" % (self.username, self.uid)

    class Meta:
        db_table = "users"
        verbose_name = "utilisateur système (NSS)"
        verbose_name_plural = "utilisateurs système (NSS)"
        get_latest_by = 'uid'

    def save(self, force_insert=False, force_update=False, force_source=False):
        """
        Enregistre ou modifie un utilisateur dans la table ``users``.

        La methode User.save() effectue quelques vérifications et modification
        avant de procéder à l'enregistrement réel de l'utilisateur dans la base
        de données :

         * si l'utilisateur (indiqué par son uid) existe déjà, les champs
           ``username`` et ``source`` ne seront pas modifiés
         * si ``source`` n'est pas 'LOCAL', alors l'enregistrement n'est pas
           effectué, sauf si on précise *force_source=True* lors de l'appel à
           *save()*
         * si aucun ``uid`` n'est imposé, alors on en calcule un nouveau, qui
           doit être supérieur à ``conf.MIN_UID`` (configurable dans le fichier 
           ``conf.py``)
         * si le ``homedir`` n'est pas précisé, on le calcule à travers une
           fonction ``homedir(self)``, qui peut être personnalisée dans le
           fichier ``conf.py``
         * si le mot de passe est livré en clair, on le crypte
        
        Ce n'est qu'après toutes ces opérations que l'enregistrement est
        effectué.
        """
        # surcharges avant enregistrement :
        # on interdit les changements sur "username" ou "source" avec ça :
        try:
            # si l'objet existe déjà, on récupère ses données actuelles
            current = User.objects.get(pk=self.pk) 
            # on refuse de modifier l'uid ou la source, il y a trop
            # d'implications par ailleurs
            self.uid = current.uid
            self.source = current.source
        except:
            pass
        # on enregistre que si la source est 'LOCAL' (pour forcer
        # l'enregistrement, il faut ajouter un force_source=True lors de
        # l'appel)
        if self.source != "LOCAL" and not force_source:
            return
        # si l'objet n'a pas d'UID proposé, on en calcule un,
        # en sachant qu'il doit être plus grand que MIN_UID
        if self.uid == None:
            try:
                self.uid = max(User.objects.latest().uid + 1, MIN_UID)
            except:
                self.uid = MIN_UID
        # si le homedir n'a pas été précisé, on le calcule
        if self.homedir == HOME_BASE:
            self.homedir = homedir(self)
        # on crypte le mot de passe (si besoin)
        self.password = password_crypt( self.password )
        # et on lance l'enregistrement via la méthode mère
        return super(User, self).save(force_insert, force_update)

    def active(self):
        return self.expire >= datetime.date.today()
    active.short_description = "Actif ?"
    active.boolean = True
    active.admin_order_field = 'expire'

    def colored_expire(self):
        if self.expire == ExpireField.INFINITY:
            return u'<span style="color: green;">jamais</span>'
        delta = (self.expire - datetime.date.today()).days
        if delta < 0:
            style = "text-decoration: line-through;"
        elif delta < 8:
            style = "color: red;"
        elif delta < 15:
            style = "color: orange;"
        else:
            style = "color: green;"
        return u'<span style="%s">%s (%s)</span>' % (style, self.expire, delta)
    colored_expire.short_description = "Expire le"
    colored_expire.allow_tags = True
    colored_expire.admin_order_field = 'expire'

    def groups(self):
        """
        Retourne la liste de tous les groupes auquel appartient
        un utilisateur (groupe principal et groupes secondaires)
        """
        groups=[self.gid]
        groups.extend(self.secgroups.all())
        return groups


class Group(models.Model):
    """
    Représentation d'un groupe au sens Unix (nss):

     * ``gid`` : numéro identifiant le groupe
     * ``name`` : nom du groupe, uniquement composé de lettres minuscules et de chiffres
     * ``password`` : mot de passe du groupe, en général pas utilisé et donc positionné à 'x'
    """
    name = models.CharField("nom du groupe", max_length=32, unique=True,
            help_text="Indiquez un identifiant de groupe, uniquement composé de lettres minuscules et de chiffres")
    password = models.CharField("mot de passe (crypté)", max_length=64, default='x', editable=False)
    gid = models.AutoField("groupID", primary_key=True) 
    # utilisateurs qui ont ce groupe en secondaire
    users_secgroup = models.ManyToManyField("User", related_name='users_secgroup', through='GroupList', blank=True)

    def __unicode__(self):
        """Représentation d'un groupe : son nom suivi de son gid"""
        return "%s (%s)" % (self.name, self.gid)

    class Meta:
        db_table = "groups"
        verbose_name = "groupe système (NSS)"
        verbose_name_plural = "groupes système (NSS)"
        get_latest_by = 'gid'

    def save(self, force_insert=False, force_update=False):
        """
        Enregistre ou modifie un groupe dans la table ``groups``.

        Si aucun gid n'est proposé, la methode Group.save() en calcule un
        avant de procéder à l'enregistrement réel du groupe dans la base.
        """
        # si l'objet n'a pas de GID proposé, on en calcule un,
        # en sachant qu'il doit être plus grande que MIN_GID
        if self.gid == None:
            try:
                self.gid = max(Group.objects.latest().gid + 1, MIN_GID)
            except:
                self.gid = MIN_GID
        # on crypte le mot de passe (si besoin)
        self.password = password_crypt( self.password )
        # et on enregistre l'objet "pour de vrai"
        return super(Group, self).save(force_insert, force_update)


    def users(self):
        """
        Retourne la liste des utilisateurs compris dans ce groupe,
        que ce groupe soit leur groupe primaire ou secondaire.
        """
        users=[]
        for user in self.user_set.all():
            users.append(user)
        for user in self.users_secgroup.all():
            users.append(user)
        return users


class GroupList(models.Model):
    """
    Association entre un *User* et un *Group* afin de connaître les groupes
    secondaires auxquels appartient un utilisateur donné.
    """
    gid = models.ForeignKey(Group, db_column="gid")
    username = models.ForeignKey(User, db_column="username")

    def __unicode__(self):
        return "%s dans %s" % (self.username, self.gid)

    class Meta:
        db_table = "grouplist"
        verbose_name = "appartenance groupe secondaire"
        verbose_name_plural = "appartenances groupes secondaires"
        unique_together = ( "gid", "username" )

