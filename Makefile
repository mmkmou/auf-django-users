APPDIR = $(DESTDIR)/usr/share/python-support/auf-django-users/aufusers
SHAREDIR = $(DESTDIR)/usr/share/auf-django-users
CONFDIR = $(DESTDIR)/etc/auf-django-users
BINDIR = $(DESTDIR)/usr/bin
LOCALDIR = $(DESTDIR)/usr/lib/auf-django-users

clean:
	rm -f *.py[co] */*.py[co]
	cd doc && make clean

install: sphinx
	mkdir -p $(APPDIR) $(CONFDIR) $(BINDIR) $(SHAREDIR) $(LOCALDIR)
	# on copie les applications et leur dépendances
	for appli in nss lib \
		     settings.py urls.py __init__.py ; do \
		cp -r $$appli $(APPDIR); \
	done
	# on copie les données "statiques"
	for share in media templates aufusers.wsgi ; do \
		cp -r $$share $(SHAREDIR); \
	done
	#
	# le script manage.py de gestion django, adapté à auf-django-users
	cp auf-django-users-manage.py $(BINDIR)
	#
	# contribs
	cp -r contrib $(LOCALDIR)
	#
	# configurations
	cp conf.py apache.conf $(CONFDIR)
	# la conf de contrib.mail sera dans /etc/auf-django-users/
	mv $(LOCALDIR)/contrib/mail/conf.py $(CONFDIR)/contrib.mail.conf.py

sphinx:
	if which sphinx-build; then \
		cd doc && make html; \
	else \
		mkdir -p doc/_build/html; \
	fi

uninstall:
	rm -rf $(APPDIR)
	rm -rf $(CONFDIR)
	rm -rf $(SHAREDIR)
	rm -rf $(LOCALDIR)
	rm -rf $(BINDIR)/auf-django-users-manage.py

