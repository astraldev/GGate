## Process this file with automake to produce Makefile.in
ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

SUBDIRS = bin glogic po data examples help

EXTRA_DIST = \
	README\
	COPYING\
	ChangeLog\
	AUTHORS\
	INSTALL\
	NEWS \
	$(INTLTOOL_FILES)

DISTCLEANFILES = intltool-extract \
	intltool-merge \
	intltool-update \
	po/.intltool-merge-cache
