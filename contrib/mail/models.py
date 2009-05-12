# -*- encoding: utf-8 -*-
"""
Gestion d'une table d'utilisateur de la messagerie. Elle peut être
synchronisée avec la gestion des utilisateurs *aufusers.nss.models.User*.
"""

from django.db import models
from aufusers.lib.expire import ExpireField
from aufusers.lib.utils import password_crypt
# pour connexion avec le module de gestion des comptes nss
from django.db.models.signals import post_save, post_delete
from aufusers.nss.models import User

# import de la configuration
from conf import DOMAINE, MAILDIR_BASE, MAIL, sync_nss2mail

try:
    from conf import mail
except:
    def mail(user):
        return "%s@%s" % (user.username, DOMAINE)

try:
    from conf import addr_from
except:
    def addr_from(user):
        return mail(user)

try:
    from conf import maildir
except:
    def maildir(user):
        return "%s/%s" % (MAILDIR_BASE, user.username)

# fin import configuration


class MailUser(models.Model):
    """
    Représente un utilisateur de messagerie :

     * ``username`` : nom d'utilisateur (identifiant de messagerie). C'est la *clé primaire*
     * ``password`` : mot de passe (crypté) 
     * ``expire`` : date d'expiration du compte
     * ``fullname`` : nom et prénom, sous la forme Prenom NOM
     * ``maildir`` : répertoire du mail (au format Maildir)
     * ``mail`` : adresse de courriel en entrée
     * ``addr_from`` : adresse d'expéditeur (en général, la même)
     * ``source`` : source des informations (== 'LOCAL' pour un utilisateur géré par le système ``aufuser``)

    Les champs ``password``, ``expire`` et ``fullname`` peuvent être fournis et mis à jour
    automatiquement lors d'une modification de l'utilisateur *nss* correspondant au ``username``.
    """
    username = models.CharField("nom d'utilisateur", max_length=128, primary_key=True,
            help_text="Indiquez un identifiant de messagerie")
    password = models.CharField("mot de passe (crypté)", max_length=64, default='x')
    expire = ExpireField("date d'expiration")
    fullname = models.CharField("nom complet", max_length=128, blank=True,
            help_text="Indiquez le nom et le prénom, sous la forme Prenom NOM (sans aucun accent)")
    maildir = models.CharField("répertoire du mail (maildir)", max_length=256,
            default=MAILDIR_BASE,
            help_text="Laissez à <em>" + MAILDIR_BASE + "</em> et la valeur sera calculée automatiquement")
    mail = models.EmailField("adresse courriel", max_length=128, unique=True,
            default=MAIL,
            help_text="Laissez à <em>@" + DOMAINE + "</em> et la valeur sera calculée automatiquement")
    addr_from = models.EmailField("adresse courriel émetteur", max_length=128,
            default=MAIL,
            help_text="Laissez à <em>@" + DOMAINE + "</em> et la valeur sera calculée automatiquement")
    source = models.CharField("source", max_length=10, default="LOCAL")

    def __unicode__(self):
        return "%s (%s)" % (self.mail, self.fullname)

    def save(self, force_insert=False, force_update=False, force_source=False):
        """
        Enregistre ou modifie un utilisateur de messagerie dans la base de données mailusers.

        La methode MailUser.save() effectue quelques vérifications et
        modification avant de procéder à l’enregistrement dans la base de
        données :

         * si source n’est pas ‘LOCAL’, alors l’enregistrement n’est pas
           effectué, sauf si on précise force_source=True lors de l’appel à
           save()
         * si le ``mail`` n’est pas précisé, on le calcule à travers une
           fonction ``mail(self)``, qui peut être personnalisée dans le fichier
           ``conf.py``
         * même chose avec les champs ``addr_from`` et ``maildir``, avec les
           fonctions ``addr_from(self)`` et ``maildir(self)``, respectivement
         * si le mot de passe est livré en clair, on le crypte

        Ce n’est qu’après toutes ces opérations que l’enregistrement est effectué
        dans la base de données.
        """
        # surcharges avant enregistrement :
        # TODO : synchro vers nss
        # par défaut, on n'enregistre que si la source est 'LOCAL' (pour forcer
        # l'enregistrement, il faut ajouter un force_source=True lors de l'appel)
        if self.source != "LOCAL" and not force_source:
            return
        # ... idem pour le mail
        if self.mail == MAIL:
            self.mail = mail(self)
        # ... et pour l'adresse d'expediteur
        if self.addr_from == MAIL:
            if self.mail == MAIL: # si un mail a été fourni, on le prend
                self.addr_from = addr_from(self)
            else:
                self.addr_from = self.mail
        # si le maildir n'a pas été précisé, on le calcule
        if self.maildir == MAILDIR_BASE:
            self.maildir = maildir(self)
        # on crypte le mot de passe (si besoin)
        self.password = password_crypt( self.password )
        # et on lance l'enregistrement réel
        return super(MailUser, self).save(force_insert, force_update)

    class Meta:
        db_table = "mail_users"
        verbose_name = "compte de messagerie"
        verbose_name_plural = "comptes de messagerie"

    def active(self):
        return self.expire >= datetime.date.today()
    active.short_description = "Actif ?"
    active.boolean = True
    active.admin_order_field = 'expire'

    def colored_expire(self):
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


# 
# synchro nss vers mail :
# fonctions qui vont écouter l'activité sur nss.User
#

def user_post_save(sender, **kwargs):
    """
    Cette procédure est automatiquement lancée après chaque création ou
    modification d'un abonné - elle utilise pour cela le signal ``post_save``
    de User.
    
    C'est elle qui effectue la synchronisation entre User et MailUser,
    en fonction des indications de ``conf.sync_nss2mail``
    """
    user = kwargs['instance']
    sync_all = 'all' in sync_nss2mail
    try:
        mailuser = MailUser.objects.get(username=user.username)
        # petite protection: on ne fait rien si les sources de user
        # et mail divergent
        if mailuser.source != user.source:
            return
    except MailUser.DoesNotExist:
        if 'create' in sync_nss2mail or sync_all:
            MailUser( username = user.username,
                      password = user.password,
                      expire = user.expire,
                      fullname = user.gecos,
                      source = user.source, ).save(force_source=True)
    else:
        if 'password' in sync_nss2mail or sync_all:
            mailuser.password = user.password
        if 'expire' in sync_nss2mail or sync_all:
            mailuser.expire = user.expire
        if 'fullname' in sync_nss2mail or sync_all:
            mailuser.fullname = user.gecos
        mailuser.save(force_source=True)
        

# connexion au signal "abonné enregistré"
post_save.connect(user_post_save, sender=User)


def user_post_delete(sender, **kwargs):
    """
    Cette procédure est lancée après chaque suppression d'un abonné (connexion
    au signal ``post_delete``)
    
    Elle supprime le compte mailuser correspondant s'il existait.

    **ATTENTION** : cette methode n'est pas appelée lors d'un QuerySet.delete()
    sur des objets User ! Il faut donc TOUJOURS supprimer les User un par un.
    Par exemple : ::

      User.objects.all().delete()   # Ne supprimera pas les comptes MailUser !
      for u un User.objects.all():
          u.delete()     # C'est bon (moins efficace, c'est vrai)
    """
    if 'create' in sync_nss2mail or 'all' in sync_nss2mail:
        user = kwargs['instance']
        try:
            MailUser.objects.get(username=user.username).delete()
        except:
            pass

# connexion au signal "abonné supprimé"
# RAPPEL : ce signal est lancé uniquement lorsqu'on efface un objet ; il n'est
# pas lancé lors d'un QuerySet.delete() !
post_delete.connect(user_post_delete, sender=User)

