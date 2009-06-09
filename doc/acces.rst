Gestion des droits d'accès 
==========================

Une fois l'application mise en ligne, il faut définir quels sont les
utilisateurs qui y auront accès, et quels seront leurs droits sur les données.

Pour cela, il faut gérer les *utilisateurs Django* de l'application. Cette
gestion se fait en tant qu'administrateur de l'application, à l'adresse
http://adresse_du_site/admin/auth/

    .. image:: acces-accueil.*

La technique la plus efficace est :
 #. Créer un ou plusieurs groupes ayant accès à certaines possibilités de l'application, par exemple la création et la modification des comptes ;
 #. Créer des utilisateurs et les faire appartenir à tel ou tel groupe afin de leur donner les accès correspondants.


Création d'un groupe de gestion
--------------------------------

Un groupe est juste une association entre un nom (le nom du groupe) et un
ensemble de droits.

Chaque modèle de donnée de chaque application Django dispose de trois droits
d'accès : ajouter, modifier et effacer un objet. Ainsi, dans l'application
``auf-django-users`` existent les droits suivants :

 * « ``nss | utilisateur système (NSS) | Can add`` » : droit d'ajouter un utilisateur NSS
 * « ``nss | utilisateur système (NSS) | Can change`` » : droit de modifier un utilisateur NSS existant 
 * « ``nss | utilisateur système (NSS) | Can delete`` » : droit de supprimer un utilisateur NSS

Pour créer un groupe d'utilisateurs qui gérent les abonnés au quotidien, on
ajoute un groupe nommé « Créateurs de comptes » et on lui attribue les droits
d'ajout et de modification sur les comptes :

    .. image:: acces-groupe.*

Création d'un utilisateur dans ce groupe
----------------------------------------

Il faut ensuite créer des utilisateurs dans le groupe. Lors de la création d'un
utilisateur, il faut veiller à deux choses. Tout d'abord, cocher la case **«
Status équipe »** qui permettra à l'utilisateur de se connecter au site (vers
le milieu de la page lorsqu'on crée un utilisateur) :

    .. image:: acces-statut-equipe.*

puis placer l'utilisateur dans le (ou les) groupe(s) désiré(s), en les cochant
dans la liste proposée à la fin de la page de création d'un utilisateur :

    .. image:: acces-coche-groupe.*

L'utilisateur ainsi créé peut ajouter et modifier des comptes utilisateurs sur
le système NSS.

Autres droits d'accès
---------------------

Il peut être utile qu'un utilisateur accès au système de logs fourni par
*contrib.log*, afin de voir les actions qui ont pu être entreprises sur tel ou
tel compte utilisateur (NSS) par le passé.

Pour permettre à un utilisateur de voir les logs, il faut lui donner les droits
de *modification* sur ce système, c'est-à-dire ajouter le droit « ``log | suivi
d'un compte | Can change ...`` ».

Note : en fait, la programmation du système de log dans l'application fait
qu'il est impossible à l'utilisateur de réellement modifier un log, mais il
peut en afficher la liste et les détails.

