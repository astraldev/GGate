AC_PREREQ([2.64])
AC_INIT(glogic, 2.6)
AM_INIT_AUTOMAKE
AM_PATH_PYTHON(3.1)

GETTEXT_PACKAGE=glogic
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [GETTEXT package name])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

AM_INIT_AUTOMAKE([1.11])
AC_CONFIG_MACRO_DIR([m4])
AS_AC_EXPAND(DATADIR, $datadir)

bzrrev=""
if test -d "$srcdir/.bzr"; \
then \
	echo This is a development branch && \
	cd $srcdir && \
	bzrrev=`$srcdir/missing --run bzr revno` \
	|| echo Failed to get revision number >&2 \
else \
	echo This is a released software; \
fi

AC_SUBST(BZRREV, $bzrrev)

YELP_HELP_INIT

AC_CONFIG_FILES([
Makefile
bin/Makefile
bin/glogic
glogic/Makefile
glogic/config.py
glogic/Components/Makefile
help/Makefile
po/Makefile.in
data/Makefile
data/icons/Makefile
data/icons/scalable/Makefile
data/images/Makefile
data/images/components/Makefile
examples/Makefile
])

AC_OUTPUT
