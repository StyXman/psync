#! /usr/bin/env python

import setup

version= setup.data['version']

for filename, template in (
	('tarball', "http://plantalta.homelinux.net/~mdione/projects/psync/dist/psync-%s.tar.gz\n"),
	('version', "%s\n"),
	):
    f= file (filename, 'w+')
    f.write (template % version)
    f.close ()
