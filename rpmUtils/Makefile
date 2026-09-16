include ../Config.mak

PACKAGE = $(shell basename `pwd`)
PYFILES = $(wildcard *.py) paths.py
PYVER := $(shell $(PYTHON) -c 'import sys; print "%.3s" %(sys.version)')
PYSYSDIR := $(shell $(PYTHON) -c 'import sys; print sys.prefix')
PYLIBDIR = $(PYSYSDIR)/lib/python$(PYVER)
PKGDIR = $(PYLIBDIR)/site-packages/$(PACKAGE)

all: $(PATHSPY)

.PHONY: all clean install

clean:
	rm -f *.pyc *.pyo *~ paths.py

install: $(PATHSPY)
	$(MKDIR) -p $(DESTDIR)/$(PKGDIR)
	for p in $(PYFILES) ; do \
		$(INSTALL) -m 644 $$p $(DESTDIR)/$(PKGDIR)/$$p; \
	done
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)/$(PKGDIR)', 1, '$(PKGDIR)', 1)"
