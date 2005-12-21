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
    parser.add_option ('-d', '--distro', action='append')
    parser.add_option ('-f', '--config-file', default='psync.conf.py')
    parser.add_option ('-g', '--debug', action='store_true', default=False)
    parser.add_option ('-j', '--subject', default='Updates del día %(date)s')
    parser.add_option ('-l', '--limit', type='int', default=20)
    parser.add_option ('-m', '--mail-to')
    parser.add_option ('-n', '--dry-run', action='store_true', default=False)
    parser.add_option ('-p', '--progress', action='store_true', default=False)
    parser.add_option ('-q', '--quiet', action='store_false', default=False)
    parser.add_option ('-s', '--save-space', action='store_true', default=False)
    parser.add_option ('-t', '--consistent', dest='save_space',
                       action='store_false', default=True)
    parser.add_option ('-v', '--verbose', action='store_true')
    return parser.parse_args ()

def main ():
    (conf, args)= handleOpts ()

    # load config file
    configVars= {}
    execfile(conf.config_file, configVars)
    config= configVars['config']
    del configVars

    if conf.distro is not None:
        distros= [ x for x in config if x['local'] in conf.distro ]
    else:
        distros= config

    mail= []
    if conf.dry_run and conf.verbose:
        print "doing dry run!"
    try:
        for distro in distros:
            distro.update (confToDict (conf))
            if conf.verbose:
                print "processing distro "+ str(distro)

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
