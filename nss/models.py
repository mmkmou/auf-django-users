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

# import de la configuration
from aufusers.conf import SHELLS, HOME_BASE, MIN_UID, DEFAULT_GID

# importe la fonction homedir() depuis la conf si elle existe,
# sinon on crée une fonction homedir() par défaut
try:
    from aufusers.conf import homedir
except:
    def homedir(user):
        return "%s/%s" % (HOME_BASE, user.username)

# même chose pour le calcul du champ expire par défaut
try:
    from aufusers.conf import default_expire
except:
    def default_expire(): 
	# fin du mois actuel (j'ai pas mieux comme algo, j'ai peu de neurone)
        # on se place au debut du mois actuel, on va 32 plus tard,
        # on prend le premier jour du mois obtenu... et on recule d'un jour. Ouf.
        return ( datetime.date.today().replace(day=1) + \
                 datetime.timedelta(32) ).replace(day=1) - datetime.timedelta(1)

# fin de l'import de la configuration

class Group(models.Model):
    """
    Représentation d'un groupe au sens Unix (nss):

     * ``gid`` : numéro identifiant le groupe
     * ``name`` : nom du groupe, uniquement composé de lettres minuscules et de chiffres
     * ``password`` : mot de passe du groupe, en général pas utilisé et donc positionné à 'x'
    """
    gid = models.AutoField("groupID", primary_key=True) 
    name = models.CharField("nom du groupe", max_length=32, unique=True,
            help_text="Indiquez un identifiant de groupe, uniquement composé de lettres minuscules et de chiffres")
    password = models.CharField("mot de passe (crypté)", max_length=64, default='x', editable=False)

    class Meta:
        db_table = "groups"
        verbose_name = "groupe système"
        verbose_name_plural = "groupes système"

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.gid)


class User(models.Model):
    """
        Représentation d'un utilisateur au sens Unix (nss). Voici les champs disponibles :

         * ``username`` : nom de l'utilisateur, uniquement composé de lettres minuscules et de chiffres. C'est la *clé primaire*
         * ``uid`` : numéro identifiant l'utilisateur
         * ``password`` : mot de passe de l'utilisateur, crypté
         * ``expire`` : date d'expiration du compte. Il s'agit d'un objet *datetime.date*
         * ``gid`` : objet Group auquel appartient l'utilisateur
         * ``gecos`` : nom et prénom, sous la forme Prenom NOM (sans aucun accent)
         * ``homedir`` : répertoire personnel ($HOME)
         * ``shell`` : interpréteur de commande
         * ``groups`` : liste des groupes secondaires auquel appartient l'utilisateur (c'est un *ManyRelatedManager*)
         * ``lstchg`` : date du dernier changement du mot de passe (*datetime.date*)
         * ``min`` : nombre de jours à attendre avant de pouvoir changer le mot de passe
         * ``warn`` : nombre de jours d'avertissement avant la fin mot de passe
         * ``max`` : nombre de jours après lesquels le mot de passe doit être changé
         * ``inact`` : nombre de jours après la fin de validité provoquant la désactivation du compte
         * ``flag`` : champ réservé
         * ``source`` : source des données de cet utilisateur (== 'LOCAL' si l'utilisateur est géré par l'application)
         * ``creation`` : date de création de l'utilisateur dans la base de donnée
         * ``modification`` : date de la dernière modification des données de l'utilisateur

    """

    username = models.CharField("nom d'utilisateur", max_length=128, primary_key=True,
            help_text="Indiquez un identifiant de connexion, uniquement composé de lettres minuscules et de chiffres")
    uid = models.IntegerField("userID", unique=True) 
    password = models.CharField("mot de passe (crypté)", max_length=64, default='x')
    expire = ExpireField("date d'expiration", default=default_expire)
    gid = models.ForeignKey("Group", db_column= "gid", default=DEFAULT_GID,
            help_text="Ne modifiez que si vous savez exactement ce que vous faîtes !")
    gecos = models.CharField("informations GECOS", max_length=128, blank=True,
            help_text="Indiquez le nom et le prénom, sous la forme Prenom NOM (sans aucun accent)")
    homedir = models.CharField("répertoire personnel (home)", max_length=256,
            default=HOME_BASE, unique=True,
            help_text="Laissez à <em>" + HOME_BASE + "</em> et la valeur sera calculée automatiquement")
    shell = models.CharField("interpréteur de commande (shell)", max_length=64, 
            choices=SHELLS, default=SHELLS[0][0], blank=False)
    groups = models.ManyToManyField("Group", related_name='groups', through='GroupList', blank=True)
    # informations shadow (non utilisées pour l'instant)
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
    flag = models.IntegerField("réservé", default = 0)
    # champs spécifiques "auf" : source de provenance des données et dates automatiques
    source = models.CharField("source", max_length=10, default="LOCAL")
    creation = models.DateTimeField("date de création", auto_now_add=True)
    modification = models.DateTimeField("dernière modification", auto_now=True)


    def __unicode__(self):
        return "%s (%s)" % (self.username, self.uid)

    def save(self, force_insert=False, force_update=False, force_source=False):
        """
        Enregistre ou modifie un utilisateur dans la base de données ``users``.

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
        # si l'objet n'a pas d'UID proposée, on en calcule une,
        # en sachant qu'elle doit être plus grande que MIN_UID
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

    class Meta:
        db_table = "users"
        verbose_name = "utilisateur système"
        verbose_name_plural = "utilisateurs système"
        get_latest_by = 'uid'

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


class GroupList(models.Model):
    """
    Association entre un *User* et un *Group* afin de connaître les groupes
    secondaires auxquels appartient un utilisateur donné.
    """
    username = models.ForeignKey(User, db_column="username")
    gid = models.ForeignKey(Group, db_column="gid")

    def __unicode__(self):
        return "%s dans %s" % (self.username, self.gid)

    class Meta:
        db_table = "grouplist"
        verbose_name = "appartenance groupe secondaire"
        verbose_name_plural = "appartenances groupes secondaires"
        unique_together = ( "username", "gid" )

