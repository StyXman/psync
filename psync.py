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
    parser.add_option ('-c', '--continue', action='store_true', default=False,
        help="Continue processing the databases instead of donwloading new ones.")
    parser.add_option ('-r', '--repo', action='append', dest='repos',
        help="a repo name to be processed. you can specify any number of them. if none specified, all repos defined in the config file will be processed.")
    parser.add_option ('-f', '--config-file', default='psync.conf.py',
        help="Process this config file instead of psync.conf.py in the current dir.")
    parser.add_option ('-d', '--debug', action='store_const', dest='log_level',
        const=logging.DEBUG, help="Be *very* verbose on what's being done.")
    parser.add_option ('-j', '--subject', default='Updates del día %(date)s',
        help="The subject of the mail sent.")
    parser.add_option ('-l', '--limit', type='int', default=0,
        help="Limit the bandwidth used to n KiB/s.")
    parser.add_option ('-m', '--mail-to',
        help="Send a summary mail to this email account. If not specified, the summary is printed on stdout.")
    parser.add_option ('-n', '--dry-run', action='store_true', default=False,
        help="Do a dry run: download databases, process them, but don't download any package. It does the summary. Usefull for foreseeing how much it will download.")
    parser.add_option ('-o', '--process-old', action='store_true', default=False,
        help="Process databases already downloaded. Mostly for debug purposses.")
    parser.add_option ('-p', '--progress', action='store_true', default=False,
        help="show a progress when downloading anything. Not suitable for non interactive running (e.g., from a cron job).")
    parser.add_option ('-q', '--quiet', action='store_false', default=False,
        help="Shh! Don't say anything!")
    parser.add_option ('-s', '--save-space', action='store_true',
        dest='save_space', default=False, help="Do not maintain consistency, saving space.")
    parser.add_option ('-t', '--consistent', action='store_false',
        dest='save_space', help="Maintain consistency, wasting temporarily space.")
    parser.add_option ('-v', '--verbose', action='store_const', dest='log_level',
        const=logging.INFO, help="Be verbose on what's being done.")
    return parser.parse_args ()

def main ():
    (conf, args)= handleOpts ()
    conf.debugging= conf.log_level==logging.DEBUG
    conf.verbose= conf.log_level==logging.INFO or conf.debugging
    psyncpkg.logLevel= conf.log_level

    # load config file
    configVars= {}
    execfile(conf.config_file, configVars)
    config= configVars['config']
    del configVars

    if conf.repos is not None:
        repos= [ x for x in config if x['repo'] in conf.repos ]
    else:
        repos= config

    mail= []
    if conf.dry_run:
        logger.info ("doing dry run!")
    try:
        for repo in repos:
            repo.update (confToDict (conf))
            logger.info ("processing repo "+repo['repo'])

            # prepare teh mail body
            mail.append (repo['repo'].center (75))
            mail.append (('~' * len (repo['repo'])).center (75))
            driverName= repo['driver']
            
            # instantiate a driver and process it
            DriverClass= getattr(__import__('psyncpkg.drivers.'+driverName, {},
                                 {}, [driverName]), driverName)
            driver= DriverClass(**repo)
            mail+= driver.processRepo ()

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
