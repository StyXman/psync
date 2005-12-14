#! /usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
# (c) 2004, 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# thanks to cholo

from tempfile import mkdtemp
from optparse import OptionParser
from socket import getfqdn
import sys
import smtplib
import datetime

if __name__=='__main__':
    parser= OptionParser ()
    parser.add_option ('-c', '--continue', dest='c', action='store_true',
        default=False)
    parser.add_option ('-d', '--distro', dest='d', action='append')
    parser.add_option ('-f', '--config-file', dest='f', default='psync.conf.py')
    parser.add_option ('-j', '--subject', dest='j',
        default='Updates del día %(date)s')
    parser.add_option ('-l', '--limit', dest='l', type='int', default=20)
    parser.add_option ('-m', '--mail-to', dest='m')
    parser.add_option ('-n', '--dry-run', dest='n', action='store_true',
        default=False)
    parser.add_option ('-p', '--progress', dest='p', action='store_true',
        default=False)
    parser.add_option ('-q', '--quiet', dest='v', action='store_false',
        default=False)
    parser.add_option ('-s', '--save-space', dest='t', action='store_false')
    parser.add_option ('-t', '--consistent', dest='t', action='store_true',
        default=True)
    parser.add_option ('-v', '--verbose', dest='v', action='store_true')
    (opts, args)= parser.parse_args ()

    cont= opts.c
    consistent= opts.t
    limit= opts.l
    verbose= opts.v
    distros= opts.d
    mailTo= opts.m
    dryRun= opts.n
    subject= opts.j
    progress= opts.p

    configVars= {}
    configFile= opts.f
    execfile(configFile, configVars)
    config= configVars['config']
    del configVars

    if distros is not None:
        distros= [ x for x in config if x['local'] in distros ]
    else:
        distros= config
        
    mail= []
    if dryRun and verbose:
        print "doing dry run!"
    try:
        for distro in distros:
            if verbose:
                print "processing distro "+ str(distro)
            mail.append (distro['local']+':')
            driverName= distro['driver']
            DriverClass= getattr(__import__('psyncpkg.drivers.'+driverName, {},
                                 {}, [driverName]), driverName)
            driver= DriverClass(cont=cont, consistent=consistent, limit=limit,
                verbose=verbose, dryRun=dryRun, progress=progress, **distro)
            mail+= driver.processDistro (distro)
            mail.append ('')

        if not mailTo is None:
            host= getfqdn ()
            body= '\r\n'.join (mail)
            mailFrom= "psync@"+host
            date= datetime.date(2005, 12, 12).today().isoformat()
            subject= subject % locals()
            
            mail= """From: %(mailFrom)s\r
To: %(mailTo)s\r
Subject: %(subject)s\r\n
\r
%(body)s""" % locals()
        
            server= smtplib.SMTP ('localhost')
            # print mail
            server.sendmail (mailFrom, mailTo, mail)
            server.quit ()
        else:
            print "\n".join (mail)

    except KeyboardInterrupt:
        # curl stays always in the same line
        print
