#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# exemple de fichier conf.py
# ----
# source = 'AUF'          # source de données que va gérer 'aufusers'
# host = '1.2.3.4'        # données de connexion pgsql
# user = 'machin'
# password = 'trucbidule'
# database = 'mabase'
# pays = ('sn', 'ml')  # si on veut limiter à certains pays
# ----

#import aufusers
import sys
import psycopg2
import conf
if 'pays' not in dir(conf):
    conf.pays = ()


def get_pgsql():
    """
    Retourne un dictionnaire contenant les utilisateurs AUF de la base de
    Montréal. Chaque entrée a pour clé le courriel de la personne, et pour
    valeur un dictionnaire avec les données correspondantes (nom, prenom, pays,
    mdp_crypt, etc) :
      {
        'thomas.noel@auf.org':   { 'nom': 'noel', 'prenom': 'thomas', ... },
        'moussa.nombre@auf.org': { 'nom': 'nombre', 'prenom': 'moussa', ... },
        ...
      }
    """
    try: # Connexion à la base postgresql
        cnx = psycopg2.connect( host = conf.host, database = conf.database,
                                user = conf.user, password = conf.password, )
    except:
        print "Impossible de se connecter à la base PostgreSQL"
        sys.exit(1)
    cursor = cnx.cursor()
    # Récupération des données de la table "Authentification".courriels_export2
    rows = ('courriel','redirection_courriel','mdp_crypt','pays','nom','prenom')
    if conf.pays:
        where = 'WHERE pays IN (%s)' % ','.join([ "'" + p + "'" for p in conf.pays ])
    else:
        where = ''
    cursor.execute("""SELECT %s 
                      FROM "Authentification".courriels_export2
                      %s""" % ( ','.join(rows) , where ) )
    # Transformation des résultat sous la forme d'une liste de dictionnaires :
    # liste = [ { 'nom': 'tanawa', 'prenom': 'emile', 'pays': 'sn',
    #             'courriel': 'emile.tanawa@auf.org', 'mdp_crypt': '...',
    #             'redirection_courriel': 'emile.tanawa@sn.auf.org'
    #           }, { ... }, ... ]
    liste = map( lambda rec: dict(zip(rows, rec)), cursor.fetchall() )
    cnx.close()
    # on extrait de cette liste les clés du futur dictionnaire, c-à-d les
    # champs "courriel" de chaque item de la liste
    keys = [ u['courriel'] for u in liste ]
    # et on retourne le dictionnaire qui associe les clés aux valeurs
    return dict(zip(keys, liste))


from pprint import pprint # pour les debugs

source = get_pgsql()
# ensemble (set) des identifiants :
source_set = set(source.keys())
pprint(source_set)

