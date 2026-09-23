include ../Config.mak

YUMETC=$(DESTDIR)$(SYSCONFDIR)/yum

all:
	echo "Nothing to do"

clean:
	rm -f *.pyc *.pyo *~

install:
	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/yum/
	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/yum/protected.d
	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/yum/repos.d
	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/yum/vars

	sed -e 's|\([^[:alnum:]/]\)/usr|\1$(PREFIX)|g' \
	    -e 's|\([^[:alnum:]/]\)/etc|\1$(SYSCONFDIR)|g' \
	    -e 's|\([^[:alnum:]/]\)/var|\1$(LOCALSTATEDIR)|g' \
	    yum.conf > $(YUMETC)/yum.conf
	chmod 644 $(YUMETC)/yum.conf

	$(INSTALL) -m 644 version-groups.conf $(YUMETC)/version-groups.conf

	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/logrotate.d
	$(INSTALL) -m 644 yum.logrotate $(DESTDIR)$(SYSCONFDIR)/logrotate.d/yum

	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/rc.d/init.d
	$(INSTALL) -m 755 yum-updatesd.init $(DESTDIR)$(SYSCONFDIR)/rc.d/init.d/yum-updatesd

	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/dbus-1/system.d/
	$(INSTALL) -m 755 yum-updatesd-dbus.conf $(DESTDIR)$(SYSCONFDIR)/dbus-1/system.d/yum-updatesd.conf

	$(INSTALL) -m 755 yum-updatesd.conf $(DESTDIR)$(SYSCONFDIR)/yum/yum-updatesd.conf

	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/bash_completion.d
	$(INSTALL) -m 644 yum.bash $(DESTDIR)$(SYSCONFDIR)/bash_completion.d
	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/cron.daily
	$(MKDIR) -p $(DESTDIR)$(SYSCONFDIR)/sysconfig/
	$(INSTALL) -D -m 755 0yum.cron $(DESTDIR)$(SYSCONFDIR)/cron.daily/0yum.cron
	$(INSTALL) -D -m 755 yum-cron $(DESTDIR)$(SYSCONFDIR)/rc.d/init.d/yum-cron
	$(INSTALL) -D -m 644 yum-daily.yum $(YUMETC)/yum-daily.yum
	$(INSTALL) -D -m 644 yum-weekly.yum $(YUMETC)/yum-weekly.yum
	$(INSTALL) -D -m 644 yum-cron.sysconf $(DESTDIR)$(SYSCONFDIR)/sysconfig/yum-cron
