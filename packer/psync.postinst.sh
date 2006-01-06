VERSION=2.3
DIRLIST=/usr/lib/python$VERSION/site-packages/psyncpkg

/usr/bin/python$VERSION -O /usr/lib/python$VERSION/compileall.py -q $DIRLIST
/usr/bin/python$VERSION /usr/lib/python$VERSION/compileall.py -q $DIRLIST
