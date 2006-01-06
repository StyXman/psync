# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# example config file

config= []

#########
# debian
#########
# deb http://http.us.debian.org/debian sarge             main non-free contrib
#     |<-- repoUrl                -->| |<-- release -->| |<-- modules     -->|
config.append (dict (
    repo= 'debian',
    repoUrl= 'http://http.us.debian.org/debian',
    repoDir= 'debian/debian',
    driver= 'Debian',
    releases= [ 'sarge' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'non-free', 'contrib', 'main/debian-installer' ],
    baseDirTemplate= '',
))
config.append (dict (
    repo= 'debian-security',
    repoUrl= 'http://security.debian.org/debian-security',
    repoDir= 'debian/debian-security',
    driver= 'Debian',
    # releases= [ 'woody/updates', 'sarge/updates' ],
    releases= [ 'sarge/updates' ],
    # archs= [ 'i386' ],
    archs= [ 'i386', 'sparc' ],
    modules= [ 'main', 'non-free', 'contrib' ],
    baseDirTemplate= '',
))
config.append (dict (
    repo= 'debian-non-US',
    repoUrl= 'http://non-us.debian.org/debian-non-US',
    repoDir= 'debian/debian-non-US',
    driver= 'Debian',
    # sarge is the last release that needs non-US
    releases= [ 'sarge/non-US' ],
    archs= [ 'i386', 'sparc' ],
    modules= [ 'main', 'non-free', 'contrib' ],
    baseDirTemplate= '',
))
## deb ftp://ftp.nerim.net/debian-marillat/ unstable main
config.append (dict (
    repo= 'marillat',
    # ftp sucks because it's a whole auth handshaking for each downloaded file
    repoUrl= 'ftp://ftp.nerim.net/debian-marillat',
    repoDir= 'debian/marillat',
    driver= 'Debian',
    releases= [ 'sid' ],
    archs= [ 'i386' ],
    modules= [ 'main' ],
    baseDirTemplate= '',
))
# deb http://www.backports.org/debian/ sarge-backports main
config.append (dict (
    repo= 'backports',
    repoUrl= 'http://www.backports.org/debian/',
    repoDir= 'debian/backports',
    driver= 'Debian',
    releases= [ 'sarge-backports' ],
    archs= [ 'i386' ],
    modules= [ 'main' ],
    baseDirTemplate= '',
))

###########
# mandrake
###########
config.append (dict (
    repo= 'mandrake',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official',
    repoDir= 'mandrake',
    driver= 'Urpmi',
    releases= [ '2005' ],
    # archs= [ 'i586', 'noarch' ],
    archs= [ 'i586' ],
    modules= [ 'main', 'contrib', 'jpackage' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s/%(arch)s/media/%(module)s',
    rpmDir= '.',
    hdlistTemplate= '../media_info/hdlist_%(module)s.cz',
))

# urpmi.addmedia contrib-ttu    ftp://ftp.phys.ttu.edu/pub/mandrake/ 9.2/contrib/i586          with hdlist.cz
#                \<-- repo -->| |<-- repoUrl                    -->| |<-- baseDirTemplate -->|      |<-- hdlist -->|
config.append (dict (
    repo= 'mandrake-updates',
    repoUrl= 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates',
    repoDir= 'mandrake/updates',
    driver= 'Urpmi',
    releases= [ 'LE2005' ],
    archs= [ 'i586', 'noarch' ],
    modules= [ 'main_updates' ],
    # it does not include the arch because the paths in the hdlist already has it
    baseDirTemplate= '%(release)s/%(module)s',
    rpmDir= '.',
    hdlist= 'media_info/hdlist.cz',
))
# http://plf.zarb.org/
# urpmi.addmedia plf-free http://plf.lastdot.org/plf/free/10.2 with hdlist.cz
# urpmi.addmedia plf-nonfree http://plf.lastdot.org/plf/non-free/10.2 with hdlist.cz
config.append (dict (
    repo= 'plf',
    # repoUrl= 'http://ftp.club-internet.fr/pub/linux/plf/',
    repoUrl= 'http://plf.lastdot.org/plf',
    repoDir= 'mandrake/plf',
    driver= 'Urpmi',
    distros= [ 'mandrake' ],
    releases= [ '10.2' ],
    archs= [ 'i586', 'noarch' ],
    modules= [ 'free', 'non-free' ],
    # baseDirTemplate= '%(distro)s/%(module)s/%(release)s/%(arch)s',
    baseDirTemplate= '%(module)s/%(release)s/%(arch)s',
    rpmDir= '.',
    # see http://plf.lastdot.org/plf/free/10.2/
    hdlist= '../hdlist.cz',
))

#########
# ubuntu
#########
config.append (dict (
    repo= 'ubuntu',
    repoUrl= 'http://archive.ubuntu.com/ubuntu',
    repoDir= 'ubuntu',
    driver= 'Debian',
    releases= [ 'breezy' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))
# ubuntu has updates and security!
# also, uni and multiverse are supported!
config.append (dict (
    repo= 'ubuntu-updates',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/updates',
    driver= 'Debian',
    releases= [ 'breezy-updates' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))
config.append (dict (
    repo= 'ubuntu-security',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/security',
    driver= 'Debian',
    releases= [ 'breezy-security' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))
# also has official backports!
config.append (dict (
    repo= 'ubuntu-backports',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/backports',
    driver= 'Debian',
    releases= [ 'breezy-backports' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'restricted', 'universe', 'multiverse' ],
    baseDirTemplate= '',
))

#########
# fedora
#########
#config+= [{
    #'local': 'fedora',
    #'driver': 'Yum',
    #'url': 'http://www.las.ic.unicamp.br/pub/fedora/linux/core',
    #'release': '4',
    #'arch': 'i386',
    #'modules': [ '' ],
    #'baseDir': "%(release)s/%(arch)s/os",
    #'rpmDir': 'Fedora/RPMS',
#}]

config.append (dict (
    repo= 'fedora-updates',
    repoUrl= 'http://www.las.ic.unicamp.br/pub/fedora/linux/core/updates',
    repoDir= 'fedora/updates',
    driver= 'Yum',
    releases= [ '3' ],
    archs= [ 'i386' ],
    baseDirTemplate= '%(release)s/%(arch)s',
    rpmDir= '.',
    debug= False,
    source= False,
))

# http://apt.kde-redhat.org/apt/kde-redhat/fedora/4/i386/stable/
config.append (dict (
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
