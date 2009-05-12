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
	for share in media templates aufusers.wsgi ; do \
		cp -r $$share $(SHAREDIR); \
	done
	cp -r contrib $(LOCALDIR)
	cp conf.py apache.conf $(CONFDIR)
	cp auf-django-users-manage.py $(BINDIR)

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

