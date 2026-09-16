ifndef YUM_CONFIG_MAK
YUM_CONFIG_MAK := 1
.DEFAULT_GOAL := all

ifneq ($(strip $(UNIXROOT)),)
ROOTPREFIX = /@unixroot
else
ROOTPREFIX =
endif
PREFIX = $(ROOTPREFIX)/usr
SYSCONFDIR = $(ROOTPREFIX)/etc
LOCALSTATEDIR = $(ROOTPREFIX)/var

PYTHON = python2

INSTALL = $(PREFIX)/bin/install -c
INSTALL_PROGRAM = ${INSTALL}
INSTALL_DATA = ${INSTALL} -m 644

MKDIR = $(PREFIX)/bin/mkdir

DIRVARS = ROOTPREFIX=$(ROOTPREFIX) PREFIX=$(PREFIX) SYSCONFDIR=$(SYSCONFDIR) LOCALSTATEDIR=$(LOCALSTATEDIR)

CONFIGDIR := $(dir $(lastword $(MAKEFILE_LIST)))
PATHSVARS := $(CONFIGDIR)paths.vars
PATHSPY := $(CONFIGDIR)rpmUtils/paths.py
PATHSPYIN := $(PATHSPY).in

ifneq ($(shell cat "$(PATHSVARS)" 2>/dev/null),$(DIRVARS))
$(shell printf '%s\n' "$(DIRVARS)" > "$(PATHSVARS)")
.PHONY: $(PATHSPY)
endif

$(PATHSPY): $(PATHSPYIN) $(PATHSVARS)
	@sed -e "s|@ROOTPREFIX@|$(patsubst %/,%,$(ROOTPREFIX))/|g" \
	     -e "s|@PREFIX@|$(PREFIX)|g" \
	     -e "s|@SYSCONFDIR@|$(SYSCONFDIR)|g" \
	     -e "s|@LOCALSTATEDIR@|$(LOCALSTATEDIR)|g" \
	     $< > $@

endif
