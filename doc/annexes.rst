Annexes
=======

Gestion des postes clients
--------------------------

Un poste client qui doit utiliser une base de données d'authentification
au format géré par ``auf-django-users`` peut utiliser le système ``libnss-mysql-bg``.

Voir les détails ici : http://wiki.auf.org/wikiteki/AuthentificationCentralisée/NssMysql

Le paquet **auf-poste-client-fixe** aide à la mise en place et à la configuration
de ce principe. Voir sur http://wiki.auf.org/wikiteki/AuthentificationCentralisée/AufDjangoUsers

Création des *homedir*
----------------------

L'application ``auf-django-user`` ne gère que la base de données qui contient
les données sur les utilisateurs.  **Elle n'est pas en charge de la création
des répertoires personnels des utilisateurs (homedir).**

Techniquement, cela serait difficile : l'application ne tourne pas en tant
qu'administrateur (*root*) du serveur. De plus, elle ne tourne en général
pas sur le serveur qui possède les répertoires utilisateurs (le serveur NFS).

Il faut donc utiliser une autre technique. En voici deux exemples.

Technique 1 : création du répertoire à la connexion
```````````````````````````````````````````````````

Une technique efficace est de faire communiquer les postes clients avec le
serveur NFS.

 #. Lors de la connexion de l'utilisateur, le poste client vérifie si le *homedir*
    existe ;
 #. S'il n'existe pas, le client envoie un message au serveur lui demandant
    de créer le répertoire.

Cette technique impose de modifier le système de connexion de *tous* les postes
clients d'un réseau géré en authentification centralisée. Il faut également
programmer un petit programme au niveau du serveur, qui va écouter les demandes
de création de répertoire et agir en fonction.

Hors ces inconvénients, les avantages sont intéressants : le serveur ne crée
que les répertoires des utilisateurs se connectant vraiment, et en cas de panne
ou d'effacement d'un répertoire, celui-ci sera reconstruit automatiquement.

Voir un exemple de mise en place dans le paquet *auf-poste-client-fixe* :
http://git.auf.org/?p=auf-poste-client.git;a=tree;f=auf-poste-client-fixe/auf-mkhomedir



Technique 2 : création du répertoire via une *contrib*
``````````````````````````````````````````````````````

Cette contrib n'existe pas (encore), mais on peut imaginer une contrib qui,
lorsqu'un utilisateur est créée, commande le serveur NFS et lui fait créer le
répertoire. Cette méthode évite de modifier les postes clients, mais elle
impose la création de tous les répertoires, y compris des gens qui ne vont
jamais se connecter. De plus, en cas de panne ou en cas de perte du répertoire
d'un utilisateur, il faut reprendre à la main...

