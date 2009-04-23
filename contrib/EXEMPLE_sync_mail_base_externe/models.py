# -*- encoding: utf-8 -*-

# Lorsqu'un MailUser est créé, modifié ou effacé, l'action est effectuée sur
# une seconde base MySQL (configurée dans le fichier conf.py de cette
# applicaton).
# Pour cela, cette application se connecte à la gestion des utililisateur de
# messagerie (aufusers.mail) via les signaux post_save et post_delete de
# Django.

from conf import mailhostdb, mailuserdb, mailpasswdb, maildb
import MySQLdb, time

from django.db.models.signals import post_save, post_delete
from aufusers.mail.models import MailUser

# action à executer lorsqu'un utilisateur est créé ou modifié
def extmail_save(sender, **kwargs):
    mailuser = kwargs['instance']
    mailuser.expire_int = int(time.mktime(mailuser.expire.timetuple())) / (24 * 3600)
    connexion = MySQLdb.connect(host = mailhostdb,
                                user = mailuserdb,
                                passwd = mailpasswdb,
                                db = maildb)
    cursor = connexion.cursor()
    command = """INSERT INTO users (username,mail,maildir,password,expire,fullname,addr_from,source)
                 VALUES (?,?,?,?,?,?,?,?)
                 ON DUPLICATE KEY UPDATE password=?, expire=?, fullname=?"""
    cursor.execute(command, ( # pour "insert" :
                              mailuser.username,
                              mailuser.mail,
                              mailuser.maildir,
                              mailuser.password,
                              mailuser.expire_int,
                              mailuser.fullname,
                              mailuser.addr_from,
                              mailuser.source,
                              # pour "on duplicate key" :
                              mailuser.password,
                              mailuser.expire_int,
                              mailuser.fullname, ))
    cursor.close()
    connexion.close()

# connexion de l'action à la gestion des MailUser
post_save.connect(extmail_save, sender=MailUser)


# action à executer lorsqu'un utilisateur est supprimé
def extmail_delete(sender, **kwargs):
    mailuser = kwargs['instance']
    connexion = MySQLdb.connect(host = mailhostdb,
                                user = mailuserdb,
                                passwd = mailpasswdb,
                                db = maildb)
    cursor = connexion.cursor()
    command = 'DELETE FROM users WHERE username=?'
    cursor.execute(command, ( mailuser.username, ) )
    cursor.close()
    connexion.close()

# connexion de l'action à la gestion des MailUser
post_delete.connect(extmail_delete, sender=MailUser)

