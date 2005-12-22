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

import psyncpkg

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync')
logger.setLevel(logLevel)

def sendmail (conf, mail):
    host= getfqdn ()
    body= '\r\n'.join (mail)
    mailFrom= "psync@"+host
    date= datetime.date(2005, 12, 12).today().isoformat()
    subject= conf.subject % locals()

    mail= """From: %(mailFrom)s\r
To: %(mailTo)s\r
Subject: %(subject)s\r\n
\r
%(body)s""" % locals()

    server= smtplib.SMTP ('localhost')
    # print mail
    server.sendmail (mailFrom, conf.mailTo, mail)
    server.quit ()

def confToDict (conf):
    d= {}
    # this kinda sucks
    for attr in dir (conf):
        if not attr in ('__doc__', '__init__', '__module__', '__repr__',
                        '_update', '_update_careful', '_update_loose',
                        'read_file', 'ensure_value', 'read_module'):
            d[attr]= getattr (conf, attr)

    return d

def handleOpts ():
    parser= OptionParser ()
    parser.add_option ('-c', '--continue', action='store_true', default=False)
    parser.add_option ('-d', '--distro', action='append', dest='distros')
    parser.add_option ('-f', '--config-file', default='psync.conf.py')
    parser.add_option ('-g', '--debug', action='store_const', dest='log_level',
                        const=logging.DEBUG)
    parser.add_option ('-j', '--subject', default='Updates del d�a %(date)s')
    parser.add_option ('-l', '--limit', type='int', default=0)
    parser.add_option ('-m', '--mail-to')
    parser.add_option ('-n', '--dry-run', action='store_true', default=False)
    parser.add_option ('-p', '--progress', action='store_true', default=False)
    parser.add_option ('-q', '--quiet', action='store_false', default=False)
    parser.add_option ('-s', '--save-space', action='store_true',
                        dest='save_space', default=False)
    parser.add_option ('-t', '--consistent', action='store_false',
                        dest='save_space')
    parser.add_option ('-v', '--verbose', action='store_const', dest='log_level',
                        const=logging.INFO)
    return parser.parse_args ()

def main ():
    (conf, args)= handleOpts ()
    conf.verbose= conf.log_level>0
    psyncpkg.logLevel= conf.log_level

    # load config file
    configVars= {}
    execfile(conf.config_file, configVars)
    config= configVars['config']
    del configVars

    if conf.distros is not None:
        distros= [ x for x in config if x['local'] in conf.distros ]
    else:
        distros= config

    mail= []
    if conf.dry_run:
        logger.info ("doing dry run!")
    try:
        for distro in distros:
            distro.update (confToDict (conf))
            logger.debug ("processing distro "+ str(distro))

            # prepare teh mail body
            mail.append (distro['local']+':')
            mail.append ('~' * (len (distro['local'])+1))
            driverName= distro['driver']
            
            # instantiate a driver and process it
            DriverClass= getattr(__import__('psyncpkg.drivers.'+driverName, {},
                                 {}, [driverName]), driverName)
            driver= DriverClass(**distro)
            driver.processDistro (distro)

            # add to the mail the updated files.
            mail+= driver.updatedFiles
            mail.append ('total update: %7.2f MiB' % (driver.downloadedSize/1048576.0))
            if driver.failed!=[]:
                mail.append ('')
                mail.append ('failed')
                mail+= driver.failed
            mail.append ('')
            mail.append ('')

        if not conf.mail_to is None:
            # send mail
            sendmail (conf, mail)
        else:
            print "\n".join (mail)

    except KeyboardInterrupt:
        # curl stays always in the same line
        print

if __name__=='__main__':
    main ()

# end
