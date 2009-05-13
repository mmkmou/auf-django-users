# -*- encoding: utf-8 -*-
"""
Pour chaque abonné (compte *nss*), on dispose de l'historique des modifications
de ses dates d'expiration. Cela permet(tra) de faire toutes les statistiques
possibles et imaginables.
"""

# TODO :
# * transformer cela en un système de conservation générique des modifications:
#   expire, password, homedir, ...
# * total_jours : ne faire le calcul que sur demande ? (ou bien faire les deux...)
# * ajouter des méthodes de calcul d'autres stats :
#   - combien d'abonnés de telle à telle date
#   - périodes d'abonnement d'un compte donné -> ((début,fin),(début,fin),...)


from django.db import models

import datetime

# pour connexion avec le module de gestion des comptes nss
from django.db.models.signals import post_save, post_delete
from aufusers.nss.models import User


class LogExpire(models.Model):
    """
    Un *LogExpire* représente une modification de la date d'expiration d'un certain utilisateur à un certain moment.
    Voici les champs correspondants :

     * ``username`` et ``creation`` : nom d'utilisateur et sa date de création,
       qui permettent de retrouver de quel utilisateur il s'agit. On doit
       fournir la date de création, car l'utilisateur 'toto' créé en 2009
       est différent de l'utilisateur 'toto' créé en 2004 puis supprimé en 2006.
     * ``modification`` : date de la modification (*datetime.datetime*)
     * ``expire`` : nouvelle date d'expiration (*datetime.date*)
     * ``total_jours`` : le nombre de jours d'abonnement de cet utilisateur, calculé
       en fonction de cette nouvelle date d'expiration.

    """
    username = models.CharField("nom d'utilisateur", max_length=128)
    creation = models.DateTimeField("Date de début du suivi du compte")
    modification = models.DateTimeField("Date de la mise à jour")
    expire = models.DateField("Nouvelle date d'expiration")
    total_jours = models.IntegerField("Nombre de jours d'abonnement", 
        default=0)

    class Meta:
        db_table = "log_expire"
        verbose_name = "modification d'expiration"
        verbose_name_plural = "modifications d'expiration"
        get_latest_by = "modification"

    def __unicode__(self):
        return u"%s expire le %s (modifié le %s)" % \
            (self.username, self.expire, self.modification)

    def username_creation(self):
        return u"%s (crée le %s)" % (self.username, self.creation.date())
    username_creation.short_description = 'utilisateur'
    username_creation.admin_order_field = 'username'

    def save(self, force_insert=False, force_update=False):
        """
        Enregistre une nouvelle expiration pour un compte. Juste avant
        l'enregistrement, on calcule le nouveau nombre de jours d'abonnement du
        compte, en fonction de sa nouvelle date d'expiration.
        """
        # on interdit les modification
        if self.pk != None:
            return
        # on cherche la dernière modification du compte
        try:
            current = LogExpire.objects \
                .filter( username=self.username, creation=self.creation ) \
                .latest()
            # si la date d'expiration n'a pas changé, on ne fait rien
            if current.expire == self.expire:
                return
        except LogExpire.DoesNotExist:
            # si c'est un nouveau compte (ou qu'il n'a jamais été comptabilisé)
            # alors tout commence aujourd'hui :
            self.total_jours = (self.expire - datetime.date.today()).days
            if self.total_jours < 0:
                self.total_jours = 0
        else:
            # calcul du nouveau nombre de jours en fonction de la nouvelle
            # date d'expiration, de l'ancienne et de la date d'aujourd'hui. Ouf.
            self.total_jours = current.total_jours
            today = datetime.date.today()
            if today <= self.expire:
                self.total_jours += (self.expire - max(today, current.expire)).days
            elif today <= current.expire:
                self.total_jours -= (current.expire - today).days
        return super(LogExpire, self).save(force_insert, force_update)
        # (TODO : gestion des expirations "infinies" ? bof... c'est trop particulier)

    def delete(self):
        """
        Cette methode ne fait *rien* car on interdit le delete dans les logs.

        Attention : cette méthode n'est appelée que pour un objet donné (donc
        notamment dans l'interface d'admin). Un QuerySet.delete() n'appelle pas
        cette fonction. Il reste donc très facile d'effacer une ligne de log
        en Python...
        """
        return

    @staticmethod
    def get_total_jours(user):
        """
        Retourne le nombre de jours d'abonnement d'un compte (User)
        """
        return LogExpire.objects \
            .filter( username=user.username, creation=user.creation ) \
            .latest().total_jours

    # TODO : autres fonctions static à programmer :
    #  get_intervalles(user) : renvoie une liste de (date_debut,date_fin) d'un abonnement
    #  get_nb_users(annee=None, mois=None) : ouch... peut-être en SQL "direct" ?

# 
# fonctions qui vont écouter l'activité sur les autres éléments
# et agir en fonction
#

def user_post_save(sender, **kwargs):
    """procédure lancée après chaque modification d'un abonné."""
    user = kwargs['instance']
    # on ne comptabilise que les comptes locaux
    if user.source != 'LOCAL':
        return
    LogExpire( username = user.username,
               expire = user.expire,
               creation = user.creation,
               modification = user.modification, ).save()

# connexion au signal "abonné enregistré"
post_save.connect(user_post_save, sender=User)

def user_post_delete(sender, **kwargs):
    """procédure lancée après chaque suppression d'un abonné. si le compte est
    supprimé avant son expiration, on enregistre qu'il a expiré plus tôt.
    ATTENTION : cette methode n'est pas appelé lors d'un QuerySet.delete()
    sur des objets User. Il faut donc TOUJOURS supprimer les User un par un."""
    user = kwargs['instance']
    # on ne comptabilise que les comptes locaux
    if user.source != 'LOCAL':
        return
    if datetime.date.today() < user.expire:
        LogExpire( username = user.username,
                   expire = datetime.date.today(),
                   creation = user.creation,
                   modification = user.modification, ).save()

# connexion au signal "abonné supprimé"
# RAPPEL : ce signal est lancé uniquement lorsqu'on efface un objet ; il n'est
# pas lancé lors d'un QuerySet.delete() !
post_delete.connect(user_post_delete, sender=User)

