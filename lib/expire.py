# -*- encoding: utf-8 -*-

from django.db import models
from django import forms
from django.conf import settings
import datetime, time

from django.forms.fields import DEFAULT_DATE_INPUT_FORMATS


class AdminExpireWidget(forms.TextInput):
    """widget pour champ Expire, avec des liens spécifiques ("fin du mois", etc)
    qui activent des action javascript contenues dans ExpireShortcuts.js"""

    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + "js/calendar.js",
              settings.MEDIA_URL + "js/ExpireShortcuts.js")

    def __init__(self, attrs={}):
        super(AdminExpireWidget, self).__init__(attrs={'class': 'vExpireField', 'size': '10'})


class ExpireField(models.DateField):
    """champ Expire permettant de gérer une date d'expiration. Côte application c'est
    une datetime.date normale ; côte base de donnée c'est un integer représentant le
    nombre de jours depuis le 1/1/1970"""

    __metaclass__ = models.SubfieldBase  # toujours passer par to_python

    INFINITY = datetime.date(2038, 01, 19)

    def db_type(self):
        return 'integer'

    def get_db_prep_value(self, value):
        """transforme ce qui vient de l'interface en une donnée à enregistrer
        dans la base : une date devient un nombre de jour depuis le 1/1/1970"""
        date = self.to_python(value)
        if date == self.INFINITY:
            return 0
        return time.mktime(date.timetuple()) / (24*3600)

    def to_python(self,value): 
        """transforme ce qui vient de la base de données en objet Python
        datetime.date"""
        if value is None: # si pas d'expiration : c'est hier !
            return datetime.date.today() - datetime.timedelta(1)
        # si c'est déjà une date : ne quasiment rien faire..
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        # si c'est une chaine de caractère : analyse via strptime selon un
        # ensemble de formats habituels
        if isinstance(value, (str, unicode)):
            for format in DEFAULT_DATE_INPUT_FORMATS:
                try:
                    return datetime.date(*time.strptime(value, format)[:3])
                except ValueError:
                    continue
                raise ValidationError(self.error_messages['invalid'])
        # si c'est un nombre = nombre de jour depuis le 1/1/1970
        # FIXME : gérer les exceptions ici (ValueError sur int(value))
        if int(value) == 0:
            return self.INFINITY
        else:
            return datetime.date.fromtimestamp(int(value) * 3600*24)

    def get_db_prep_lookup(self, lookup_type, value):
        # les methodes de recherche par annee, mois et jour ne fonctionnent
        # pas (en tout cas, je ne sais pas comment faire pour)
        if lookup_type in ('year', 'month', 'day'):
            raise TypeError('Lookup type %r not supported.' % lookup_type)
        else:
            return super(ExpireField, self).get_db_prep_lookup(lookup_type, value)

    def formfield(self, **kwargs):
        # on prend le formfield de DateField, mais en y forçant notre widget spécifique
        kwargs['widget'] = AdminExpireWidget
        return super(ExpireField, self).formfield(**kwargs)

