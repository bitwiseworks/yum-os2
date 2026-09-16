include ../Config.mak

all:
	echo "Nothing to do"

clean:
	rm -f *.pyc *.pyo *~
	rm -fr epydoc

install:
	$(MKDIR) -p $(DESTDIR)$(PREFIX)/share/man/man5
	$(MKDIR) -p $(DESTDIR)$(PREFIX)/share/man/man8
	$(INSTALL) -m 644 yum.8 $(DESTDIR)$(PREFIX)/share/man/man8/yum.8
	$(INSTALL) -m 644 yum-shell.8 $(DESTDIR)$(PREFIX)/share/man/man8/yum-shell.8
	$(INSTALL) -m 644 yum.conf.5 $(DESTDIR)$(PREFIX)/share/man/man5/yum.conf.5
	$(INSTALL) -m 644 yum-updatesd.8 $(DESTDIR)$(PREFIX)/share/man/man8/yum-updatesd.8
	$(INSTALL) -m 644 yum-updatesd.conf.5 $(DESTDIR)$(PREFIX)/share/man/man5/yum-updatesd.conf.5
