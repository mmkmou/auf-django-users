# -*- encoding: utf-8 -*-

import random, crypt

def password_crypt( password ):
    """reçoit un mot de passe et le renvoie crypté (md5). Ne fait rien si le
    mot de passe semble être déjà crypté ; renvoie 'x' si le mot de passe est vide
    ou déjà égal à 'x'"""
    if password in ( None, '', 'x' ):
        return "x" # mot de passe "invalide"
    elif password[0:3] == '$1$': # TODO : une regex plus restrictive
        return password # mot de passe déjà crypé
    else:
        salt = "$1$" + '' \
               .join( [ random.choice( 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' )
                    for i in xrange(8) ])
        return crypt.crypt( password, salt )

