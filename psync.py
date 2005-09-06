#! /usr/bin/python
# (c) 2004, 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# thanks to cholo

from tempfile import mkdtemp
import sys
from optparse import OptionParser

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

    # configFile= os.environ['HOME']+'.psync.conf.py'
    configVars= {}
    configFile= 'psync.conf.py'
    execfile(configFile, configVars)
    config= configVars['config']
    # print config
    del configVars

    if distros is not None:
        distros= [ x for x in config if x['local'] in distros ]
    else:
        distros= config

    finished= True

    try:
        for distro in distros:
            driverName= distro['driver']
            DriverClass= getattr(__import__('psync.drivers.'+driverName, {}, {}, [driverName]), driverName)
            driver= DriverClass(cont, consistent, limit, verbose, **distro)
            driver.processDistro (distro)

    except KeyboardInterrupt:
        finished= False
        # curl stays always in the same line
        print
    except (), e:
        try:
            print "error prcessing %s" % filename
        except:
            pass
        raise e
