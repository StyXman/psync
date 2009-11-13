# -*- coding: utf-8 -*-
# (c) 2005-2009
# Marcos Dione <mdione@grulic.org.ar>

# example config file

config= []
config1= []

#########
# debian
#########
# deb http://http.us.debian.org/debian sarge             main non-free contrib
#     |<-- repoUrl                -->| |<-- release -->| |<-- modules     -->|
config.append (dict (
    repo= 'debian',
    # repoUrl= 'http://http.us.debian.org/debian',
    # repoUrl= 'http://mirror/debian',
    # repoUrl= 'http://ftp.ie.debian.org/debian',
    repoUrl= 'http://mirrors.kernel.org/debian',
    repoDir= 'debian/debian',
    driver= 'Debian',

    # driver= 'DebianEdos',
    releases= [ 'lenny', 'squeeze', 'sid' ],
    # releases= [ 'etch'],
    # archs= [ 'i386', 'sparc', 'amd64' ],
    archs= [ 'i386', 'amd64' ],
    # archs= [ 'i386' ],
    modules= [ 'main', 'non-free', 'contrib', 'main/debian-installer' ],
    # modules= [ 'main' ],
    baseDir= '',
    # DebianEdos repos need a(nother) debian repo as reference
    # except for debian ones, which are their own reference
    # see marillat repo below
    cleanLevel= 'repo',
))
config.append (dict (
    repo= 'debian-security',
    repoUrl= 'http://security.debian.org/debian-security',
    repoDir= 'debian/debian-security',
    driver= 'Debian',
    releases= [ 'etch/updates', 'lenny/updates' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main', 'non-free', 'contrib' ],
    baseDir= '',
))
config.append (dict (
    repo= 'debian-volatile',
    repoUrl= 'http://volatile.debian.org/debian-volatile',
    repoDir= 'debian/debian-volatile',
    driver= 'Debian',
    releases= [ 'lenny/volatile' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main', 'non-free', 'contrib' ],
    baseDir= '',
))
config1.append (dict (
    repo= 'debian-non-US',
    repoUrl= 'http://non-us.debian.org/debian-non-US',
    repoDir= 'debian/debian-non-US',
    driver= 'Debian',
    # sarge is the last release that needs non-US
    releases= [ 'sarge/non-US' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'non-free', 'contrib' ],
    baseDir= '',
))

## deb ftp://ftp.nerim.net/debian-marillat/ unstable main
config1.append (dict (
    repo= 'marillat',
    # ftp sucks because it's a whole auth handshaking for each downloaded file
    repoUrl= 'ftp://ftp.nerim.net/debian-marillat',
    repoDir= 'debian/marillat',
    driver= 'DebianEdos',
    releases= [ 'sid' ],
    archs= [ 'i386' ],
    modules= [ 'main' ],
    baseDir= '',
    # DebianEdos repos need a(nother) debian repo as reference
    debianRepo= 'debian/debian',
    debianModules= [ 'main' ]
))

# deb http://www.debian-multimedia.org sarge main
# deb http://www.debian-multimedia.org etch main
# amd64, i386 and sparc
config1.append (dict (
    repo= 'debian-mm',
    repoUrl= 'http://www.debian-multimedia.org',
    repoDir= 'debian/debian-multimedia',
    driver= 'DebianEdos',
    releases= [ 'sid' ],
    archs= [ 'i386' ],
    modules= [ 'main' ],
    baseDir= '',
    # DebianEdos repos which are not Debian itself
    # need a(nother) debian repo as reference
    debianRepo= 'debian/debian',
    debianModules= [ 'main', 'non-free', 'contrib' ]
))

# deb http://www.backports.org/debian/ sarge-backports main
config.append (dict (
    repo= 'backports',
    repoUrl= 'http://www.backports.org/debian/',
    repoDir= 'debian/backports',
    driver= 'Debian',
    releases= [ 'etch-backports' ],
    # archs= [ 'i386', 'sparc', 'amd64' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main' ],
    baseDir= '',
))

# deb http://packages.debianbase.de/etch/i386/nx/ ./
config1.append (dict (
    repo= 'freenx',
    repoUrl= 'http://packages.debianbase.de/',
    repoDir= 'debian/freenx',
    driver= 'SimpleDebian',
    releases= [ 'sarge', 'etch' ],
    archs= [ 'i386' ],
    modules= [ 'nx' ],
    baseDir= '%(release)s/%(arch)s/%(module)s',
))

# test site
# deb http://snapshot.debian.net/archive pool irssi-scripts
config1.append (dict (
    repo= 'test',
    repoUrl= 'http://luon.net/debian',
    repoDir= 'debian/test',
    driver= 'DebianEdos',
    releases= [ 'sid' ],
    archs= [ 'i386' ],
    modules= [ 'main' ],
    baseDir= '',
))

# http://people.debian.org/~aurel32/BACKPORTS
config1.append (dict (
    repo= 'aurel',
    repoUrl= 'http://people.debian.org/~aurel32/BACKPORTS',
    repoDir= 'test',
    driver= 'Debian',
    releases= [ 'sarge' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main' ],
    baseDir= '',
))

config1.append (dict (
    repo= 'local-test',
    repoUrl= 'http://localhost/~mdione/test',
    repoDir= 'local-test',
    driver= 'Debian',
    releases= [ 'sarge' ],
    archs= [ 'i386', ],
    modules= [ 'main' ],
    baseDir= '',
))


###########
# mandriva
###########
config1.append (dict (
    repo= 'mandriva',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official',
    # repoUrl= 'http://ftp.heanet.ie/pub/mandrake/Mandrakelinux/official',
    repoDir= 'mandrake',
    driver= 'Urpmi',
    releases= [ '2008.1' ],
    archs= [ 'i586' ],
    # modules= [ 'main', 'non-free', 'contrib' ],
    modules= [ 'main', 'non-free' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s/%(arch)s/media/%(module)s',
    rpmDir= 'release',
    hdlistTemplate= '../media_info/hdlist_%(module)s.cz',
    # relative to repoDir
    ignore= [ 'updates' ],
))

config1.append (dict (
    repo= 'mandriva-with_jpackage',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official',
    # repoUrl= 'http://ftp.heanet.ie/pub/mandrake/Mandrakelinux/official',
    repoDir= 'mandrake',
    driver= 'Urpmi',
    releases= [ '2005', '2006.0' ],
    archs= [ 'i586' ],
    modules= [ 'main', 'contrib', 'jpackage' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s/%(arch)s/media/%(module)s',
    rpmDir= '.',
    hdlistTemplate= '../media_info/hdlist_%(module)s.cz',
    # relative to repoDir
    ignore= [ 'updates' ],
))
# urpmi.addmedia contrib-ttu    ftp://ftp.phys.ttu.edu/pub/mandrake/ 9.2/contrib/i586          with hdlist.cz
#                \<-- repo -->| |<-- repoUrl                    -->| |<-- baseDirTemplate -->|      |<-- hdlist -->|
# http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates/2007.0/i586/media/main/updates/
config.append (dict (
    repo= 'mandriva-updates',
    # repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates',
    repoUrl= 'http://mirror.fis.unb.br/pub/linux/MandrivaLinux/official/updates',
    repoDir= 'mandrake/updates',
    driver= 'Urpmi',
    # don't forget to ignore the old ones!
    releases= [ '2009.1', '2010.0' ],
    archs= [ 'i586' ],
    modules= [ 'main' ],
    baseDirTemplate= '%(release)s/%(arch)s/media/%(module)s/updates',
    rpmDir= '.',
    # relative to repoDir
    hdlistTemplate= 'media_info/hdlist.cz',
    # ignore= [ '9.2', 'LE2005', '2005', '10.2', '2006.0' ],
))
# http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates/2006.0/main_updates/
config1.append (dict (
    repo= 'mandriva-updates-without_arch',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates',
    repoDir= 'mandrake/updates',
    driver= 'Urpmi',
    # don't forget to ignore the old ones!
    releases= [ '2008.1' ],
    archs= [ 'i586' ],
    modules= [ 'main_updates' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s/%(module)s',
    rpmDir= '.',
    # relative to repoDir
    hdlist= 'media_info/hdlist.cz',
    ignore= [ '9.2', 'LE2005', '2005', '10.2' ],
))
# fucking old version
config1.append (dict (
    # http://mirrors.kernel.org/mandrake/Mandrakelinux/old/updates/2005/base/synthesis.hdlist.cz
    # http://mirrors.kernel.org/mandrake/Mandrakelinux/old/updates/2005/main_updates/media_info/
    repo= 'mandriva-updates-old',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/old/updates',
    repoDir= 'mandrake/updates',
    driver= 'Urpmi',
    # don't forget to ignore the official ones!
    releases= [ '2005' ],
    archs= [ 'i586' ],
    modules= [ 'main_updates' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s/%(module)s',
    rpmDir= '.',
    hdlist= 'media_info/hdlist.cz',
    # relative to repoDir
    ignore= [ '2006.0', 'LE2005', '10.2', '9.2', '2007.0' ],
))
# fucking different version!
config1.append (dict (
    # http://mirrors.kernel.org/mandrake/Mandrakelinux/old/updates/9.2/base/synthesis.hdlist.cz
    repo= 'mandriva-updates-old-no_modules',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/old/updates',
    repoDir= 'mandrake/updates',
    driver= 'Urpmi',
    # don't forget to ignore the official ones!
    releases= [ '9.2' ],
    archs= [ 'i586' ],
    # modules= [ 'main_updates' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s',
    rpmDir= 'RPMS',
    hdlist= 'base/hdlist.cz',
    # relative to repoDir
    ignore= [ '2006.0', 'LE2005', '10.2', '2005', '2007.0' ],
))

# http://plf.zarb.org/
# urpmi.addmedia plf-free http://plf.lastdot.org/plf/free/10.2 with hdlist.cz
# urpmi.addmedia plf-nonfree http://plf.lastdot.org/plf/non-free/10.2 with hdlist.cz
config1.append (dict (
    repo= 'rpmfusion',
    # repoUrl= 'http://ftp.club-internet.fr/pub/linux/plf/',
    # repoUrl= 'http://plf.lastdot.org/plf',
    repoUrl= 'http://mirrors.lastdot.org:1280/plf',
    repoDir= 'mandrake/plf',
    driver= 'Urpmi',
    distros= [ 'mandrake' ],
    releases= [ '2009.1' ],
    archs= [ 'i586' ],
    modules= [ 'free', 'non-free' ],
    # baseDirTemplate= '%(distro)s/%(module)s/%(release)s/%(arch)s',
    # baseDirTemplate= '%(module)s/%(release)s/%(arch)s',
    baseDirTemplate= '%(release)s/%(module)s/release/binary/%(arch)s',
    rpmDir= '.',
    # see http://plf.lastdot.org/plf/free/10.2/
    # hdlist= '../hdlist.cz',
    hdlist= 'media_info/hdlist.cz',
))

#########
# ubuntu
#########
config.append (dict (
    repo= 'ubuntu',
    repoUrl= 'http://archive.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/ubuntu',
    driver= 'Debian',
    releases= [ 'hardy', 'jaunty', 'karmic' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main', 'restricted' ],
    baseDirTemplate= '',
))
# ubuntu has updates and security!
# also, uni and multiverse are supported!
config.append (dict (
    repo= 'ubuntu-updates',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/updates',
    driver= 'Debian',
    releases= [ 'hardy-updates', 'jaunty-updates', 'karmic-updates' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))
config.append (dict (
    repo= 'ubuntu-security',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/security',
    driver= 'Debian',
    releases= [ 'hardy-security', 'jaunty-security', 'karmic-security' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))
# also has official backports!
config.append (dict (
    repo= 'ubuntu-backports',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/backports',
    driver= 'Debian',
    releases= [ 'hardy-backports', 'jaunty-backports', 'karmic-backports' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))

# kde3
# deb http://ppa.launchpad.net/kb9vqf/ubuntu intrepid main
config.append (dict (
    repo= 'ubuntu-kde3',
    repoUrl= 'http://ppa.launchpad.net/kb9vqf/ubuntu',
    repoDir= 'ubuntu/kde3',
    driver= 'Debian',
    releases= [ 'intrepid' ],
    archs= [ 'i386', 'amd64' ],
    modules= [ 'main' ],
    baseDirTemplate= '',
))

#########
# fedora
#########
config.append (dict (
    repo= 'fedora',
    # repoUrl= 'http://www.las.ic.unicamp.br/pub/fedora/linux/core',
    # repoUrl= 'http://mirrors.kernel.org/fedora/core',
    # repoUrl= 'http://fedora.c3sl.ufpr.br/linux/releases',
    repoUrl= 'http://fedora.tu-chemnitz.de/pub/linux/fedora/linux/releases',
    repoDir= 'fedora',
    driver= 'Yum',
    releases= [ '10', '11' ],
    archs= [ 'i386', 'x86_64' ],
    baseDirTemplate= '%(release)s/Fedora/%(arch)s/os',
    # rpmDir= 'Fedora/RPMS',
    rpmDir= '.',
    debug= False,
    source= False,
    ignore= [ 'updates' ],
))
config.append (dict (
    repo= 'fedora-updates',
    # repoUrl= 'http://www.las.ic.unicamp.br/pub/fedora/linux/core/updates',
    # repoUrl= 'http://mirrors.kernel.org/fedora/core/updates',
    # repoUrl= 'http://fedora.tu-chemnitz.de/pub/linux/fedora/linux/updates',
    repoUrl= 'http://ftp.uni-kl.de/pub/linux/fedora/linux/updates',
    repoDir= 'fedora/updates',
    driver= 'Yum',
    releases= [ '10', '11' ],
    archs= [ 'i386', 'x86_64' ],
    baseDirTemplate= '%(release)s/%(arch)s',
    rpmDir= '.',
    debug= False,
    source= False,
    # debugging= True,
))

# http://apt.kde-redhat.org/apt/kde-redhat/fedora/4/i386/stable/
config1.append (dict (
    repo= 'kde-redhat',
    repoUrl= 'http://apt.kde-redhat.org/apt/kde-redhat',
    repoDir= 'fedora/kde-redhat',
    driver= 'Yum',
    distros= [ 'fedora' ],
    releases= [ '4' ],
    archs= [ 'i386' ],
    modules= [ 'testing' ],
    baseDirTemplate= '%(distro)s/%(release)s/%(arch)s/%(module)s',
    rpmDir= '.',
    debug= False,
    source= False,
))


#######
# suse
#######
# http://mirrors.kernel.org/suse/update/10.1
config1.append (dict (
    repo= 'suse-updates',
    # repoUrl= 'http://mirrors.kernel.org/suse/update',
    # repoUrl= 'http://www.mirrors.net.ar/pub/suse/i386/update',
    # repoUrl= 'http://suse.mirrors.tds.net/pub/suse/update',
    # repoUrl= 'http://ftp.gwdg.de/pub/linux/suse/suse_update',
    repoUrl= 'http://afs.caspur.it/afs/italia/project/mirrors/suse/update/',
    repoDir= 'suse/updates',
    driver= 'Yum',
    # releases= [ '9.0', '9.1', '10.1' ],
    # the 9.0 release is not yum based :(
    # the 9.1 release fails decompressing the primary.xml.gz
    releases= [ '10.1', '10.2' ],
    archs= [ 'i586' ],
    baseDirTemplate= '%(release)s',
    rpmDir= '.',
    debug= False,
    source= False,
    # relative to repoDir
    ignore= [ '9.0', '9.1' ],
))


########
# slack
########
# http://mirror.slacklife.com.br/slackware-current/
config1.append (dict (
    repo= 'slackware',
    repoUrl= 'http://ftp.gwdg.de/pub/linux/slackware',
    repoDir= 'slackware',
    driver= 'Slack',
    releases= [ '10.2', '11.0', 'current' ],
    modules= [ 'slackware', 'extra' ],
    baseDirTemplate= 'slackware-%(release)s',
))

#################
# OpenOffice.org
#################
# http://ftp.snt.utwente.nl/pub/software/openoffice/
config.append (dict (
    repo= 'ooffice',
    repoUrl= 'http://ftp.snt.utwente.nl/pub/software/openoffice',
    repoDir= 'ooffice',
    driver= 'OpenOfficeOrg',
    releases= [ '3.0.1' ],
    archs= [ 'LinuxIntel', 'Win32Intel', 'SolarisSparc', 'Solarisx86' ],
    exts= [ 'tar.gz', 'exe', 'tar.gz', 'tar.gz' ],
    languages= [ 'es' ],
    subLanguages= [ [ 'ES', 'AR' ] ],
    withJRE= True,
    baseDirTemplate= '',
    filenameTemplate= 'localized/%(lang)s/%(release)s/OOo_%(release)s_%(arch)s_install_%(lang)s.%(ext)s',
))

#######
# CPAN
#######
# http://ftp.snt.utwente.nl/pub/software/openoffice/
config.append (dict (
    repo= 'cpan',
    repoUrl= 'http://ftp.ndlug.nd.edu/pub/perl/',
    repoDir= 'cpan',
    driver= 'Cpan',
))

##################
# Mozilla Project
##################
# http://ftp.mozilla.org/pub/mozilla.org/
config.append (dict (
    repo= 'mozilla',
    repoUrl= 'http://ftp.mozilla.org/pub/mozilla.org/',
    repoDir= 'mozilla',
    driver= 'Mozilla',
    apps= [ ('firefox', [ '3.5.2', '3.0.13' ]), ('thunderbird', [ '3.0b2', '2.0.0.22' ]), ],
    languages= [ 'en-US', 'es-AR', ],
    archs= [ 'linux-i686', 'win32' ],
    # this really sucks
    archTemplates= [ '%(app)s-%(version)s.tar.bz2', '%(App)s%%20Setup%%20%(version)s.exe' ],
    updates= True,
))
