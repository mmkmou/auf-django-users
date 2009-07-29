#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""

Synchronisateur des comptes du système centrale de Montréal
vers une base libnss locale (pilotée via auf-django-users)

Bla bla bla de doc ...
TODO/FIXME : rendre le script résistant aux pannes

Exemple de fichier conf.py à placer dans le même répertoire que le script :
---------------
# -*- encoding: utf-8 -*-

# données de connexion vers la base PostgreSQL de Montréal
db_host = '1.2.3.4'
db_user = 'testeur'
db_password = 'passtest'
db_database = 'AUF'

# le reste est facultatif...

# si on veut restreindre à certains pays
#pays = ('ml', 'sn')
# pour un seul pays, ne pas oublier la virgule !
#pays = ('ml', )

# source aufuser à gérer
#source = 'AUF'

# date d'expiration des comptes créés
#import datetime
#expire = datetime.date(2038, 01, 19)
---------------

"""

# configuration

# valeurs par défaut
db_host = ''
db_user = 'test'
db_password = 'test'
db_database = 'AUF'
db_table = '"Authentification".courriels_export2'
pays = () # par défaut, tous les pays
source = 'AUF'
import datetime
expire = datetime.date(2038, 01, 19)
# on va chercher les vraies valeurs dans conf.py
from conf import *

import sys
import psycopg2
from aufusers.nss.models import User

def get_pgsql():
    """
    Retourne un dictionnaire contenant les utilisateurs AUF de la base de
    Montréal. Chaque entrée a pour clé le prenom.nom de la personne, et pour
    valeur un dictionnaire avec les données correspondantes (nom, prenom, pays,
    mdp_crypt, etc) :
      {
        'thomas.noel':   { 'nom': 'noel', 'prenom': 'thomas', ... },
        'moussa.nombre': { 'nom': 'nombre', 'prenom': 'moussa', ... },
        ...
      }
    """
    cnx = psycopg2.connect( host = db_host, database = db_database,
                            user = db_user, password = db_password, )
    cursor = cnx.cursor()
    # Récupération des données de la table "Authentification".courriels_export2
    rows = ('courriel','redirection_courriel','mdp_crypt','pays','nom','prenom')
    if pays:
        where = "WHERE pays IN ('%s')" % "','".join(pays)
    else:
        where = ''
    cursor.execute('SELECT %s FROM %s %s' % ( ','.join(rows), db_table, where ) )
    # Transformation des résultat sous la forme d'une liste de dictionnaires :
    # liste = [ { 'nom': 'tanawa', 'prenom': 'emile', 'pays': 'sn',
    #             'courriel': 'emile.tanawa@auf.org', 'mdp_crypt': '...',
    #             'redirection_courriel': 'emile.tanawa@sn.auf.org'
    #           }, { ... }, ... ]
    liste = map( lambda rec: dict(zip(rows, rec)), cursor.fetchall() )
    cnx.close()
    # construction des champs GECOS a partir de prenom+nom
    for u in liste:
        u['gecos'] = u['prenom'].title() + ' ' + u['nom'].upper()
    # on extrait de cette liste les clés du futur dictionnaire, c-à-d la
    # partie gauche du champ "courriel" de chaque item de la liste
    keys = [ u['courriel'].split('@')[0] for u in liste ]
    # et on retourne le dictionnaire qui associe les clés aux valeurs
    return dict(zip(keys, liste))


# fromca est la source des données
fromca = get_pgsql()
# fromca_set : ensemble des logins source
fromca_set = set(fromca)

# "local" est la cible des données
liste = User.objects.filter(source=source)
keys = [ u.username for u in liste ]
local = dict(zip(keys, liste))
# local_set : ensemble des logins cible
local_set = set(local)

# la magie des set ...
nouveaux = fromca_set - local_set
anciens = local_set - fromca_set
communs = fromca_set & local_set

for username in nouveaux:
    print username, ': création'
    u = fromca[username]
    User( username = username,
          gecos = u['gecos'],
          password = u['mdp_crypt'],
          expire = expire,
          source = source, ).save( force_source=True )

for username in anciens:
    print username, ': suppression'
    local[username].delete()

for username in communs:
    f, l = fromca[username], local[username]
    if l.password != f['mdp_crypt'] or l.gecos != f['gecos']:
        print username, ': mise à jour'
        l.password = f['mdp_crypt']
        l.gecos = f['gecos']
        l.save( force_source=True )

