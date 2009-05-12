Documentation de auf-django-users
=================================

Le système auf-django-users est un projet Django qui propose :

 * une interface Web d'accès à une base d'authentification compatibe ``libnss-mysql-bg``
 * la création d'une telle base si elle n'existe pas
 * une API permettant d'accéder aux données de la base via des objets Python
 * la possibilité d'ajouter des extensions (*contrib*), c'est-à-dire d'autres
   applications connectées à la notion d'utilisateur (mais pas seulement...)

Cette documentation explique comment mettre en place le système : mise en ligne
via le serveur Web Apache2 et connexion à une base de donnée MySQL.

.. toctree::
   :maxdepth: 2

   premiers-pas
   wsgi
   mysql
   api
   contrib


Index et tables
===============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

