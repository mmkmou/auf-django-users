Documentation de auf-django-users
=================================

Le système auf-django-users est un projet Django qui propose :

 * une interface Web d'accès à une base d'authentification compatibe ``libnss-mysql-bg``
 * une aide pour la création de cette base si elle n'existe pas
 * une API permettant d'accéder aux données de la base via des objets Python
 * la possibilité d'ajouter des extensions (*contrib*), c'est-à-dire d'autres
   applications liées à la notion d'utilisateur

.. image:: auf-django-users.*

Cette documentation décrit l'application et explique comment mettre en
production le système. Lisez-la complétement, elle ne contient pas beaucoup
de choses inutiles.
 
-----

.. toctree::
   :maxdepth: 2

   premiers-pas
   mysql
   wsgi
   acces
   api
   contrib
   annexes


Index et tables
===============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

