#! /usr/bin/python
# (c) 2004, 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# thanks to cholo

from tempfile import mkdtemp
import sys
from optparse import OptionParser

# from psync.core import Psync
from psync.debian import Debian

if __name__=='__main__':
    parser= OptionParser ()
    parser.add_option ('-c', '--continue', dest='c', action='store_true', default=False)
    parser.add_option ('-d', '--distro', dest='d', action='append')
    parser.add_option ('-l', '--limit', dest='l', type='int', default=20)
    parser.add_option ('-q', '--quiet', dest='v', action='store_false', default=False)
    parser.add_option ('-s', '--save-space', dest='t', action='store_false')
    parser.add_option ('-t', '--consistent', dest='t', action='store_true', default=True)
    parser.add_option ('-v', '--verbose', dest='v', action='store_true')
    (opts, args)= parser.parse_args ()

    cont= opts.c
    consistent= opts.t
    limit= opts.l
    verbose= opts.v
    distros= opts.d

    # syncer= Psync (cont, consistent, limit, verbose)
    syncer= Debian (cont, consistent, limit, verbose)
    syncer.main (distros)
