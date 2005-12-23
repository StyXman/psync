# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# example config file

config= []
#config+= [{
    #'local': 'debian/updates/sarge',
    #'driver': 'Debian',
    #'url': 'http://security.debian.org/debian-security',
    #'release': 'sarge/updates',
    #'arch': 'i386',
    #'modules': [ 'main', 'non-free', 'contrib' ],
#}]
#config+=[{
    #'local': 'debian-non-US',
    #'driver': 'Debian',
    #'url': 'http://non-us.debian.org/debian-non-US',
    #'release': 'sid/non-US',
    #'arch': 'i386',
    #'modules': [ 'main', 'non-free', 'contrib' ],
#}]

## deb ftp://ftp.nerim.net/debian-marillat/ unstable main
#config+= [{
    #'local': 'marillat',
    #'driver': 'Debian',
    #'url': 'ftp://ftp.nerim.net/debian-marillat',
    #'release': 'sid',
    #'arch': 'i386',
    #'modules': [ 'main' ],
#}]

#config+= [{
    #'local': 'plf-free',
    #'driver': 'Urpmi',
    #'url': 'http://ftp.club-internet.fr/pub/linux/plf/mandrake/free',
    #'release': '10.2',
    #'distroSpec': '%(release)s',
    #'rpmSpec': '%(arch)s',
    #'arch': 'i586',
    #'modules': [''],
    #'hdlist': '../synthesis.hdlist.cz',
#}]

#config+= [{
    #'local': 'mandrake',
    #'driver': 'Urpmi',
    #'url': 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official',
    #'release': '2005',
    #'arch': 'i586',
    #'distroSpec': '%(release)s/%(arch)s',
    #'rpmSpec': 'media/%(module)s',
    #'modules': [ 'main', 'contrib', 'jpackage' ],
    #'hdlist': '../media_info/synthesis.hdlist_%(module)s.cz',
#}]

#config+= [{
    #'local': 'mandrake/updates',
    #'driver': 'Urpmi',
    #'url': 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates',
    #'release': 'LE2005',
    #'arch': 'i586',
    #'distroSpec': '%(release)s',
    #'rpmSpec': 'main_updates',
    #'modules': [ '' ],
    #'hdlist': 'media_info/synthesis.hdlist.cz',
#}]

## ubuntu
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

#config+= [{
    #'local': 'ubuntu/updates/hoary',
    #'driver': 'Debian',
    #'url': 'http://security.ubuntu.com/ubuntu',
    #'release': 'hoary-security',
    #'arch': 'i386',
    #'modules': [ 'main' ],
#}]
config.append (dict (
    repo= 'ubuntu-updates',
    repoUrl= 'http://security.ubuntu.com/ubuntu',
    repoDir= 'ubuntu/updates',
    driver= 'Debian',
    releases= [ 'breezy-security' ],
    archs= [ 'i386' ],
    modules= [ 'main', 'restricted' ],
    baseDirTemplate= '',
))


#config+= [{
    #'local': 'ubuntu-warty',
    #'driver': 'Debian',
    #'url': 'http://archive.ubuntu.com/ubuntu',
    #'release': 'warty',
    #'arch': 'i386',
    #'modules': [ 'main', 'restricted', 'universe' ],
#}]

#config+= [{
    #'local': 'ubuntu/updates/breezy',
    #'driver': 'Debian',
    #'url': 'http://security.ubuntu.com/ubuntu',
    #'release': 'breezy-security',
    #'arch': 'i386',
    #'modules': [ 'main' ],
#}]

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

#config+= [{
    #'local': 'fedora/updates',
    #'driver': 'Yum',
    #'url': 'http://www.las.ic.unicamp.br/pub/fedora/linux/core/updates',
    #'release': '3',
    #'arch': 'i386',
    #'modules': [ '' ],
    #'baseDir': "%(release)s/%(arch)s",
    #'rpmDir': '.',
#}]

config.append (dict (
    repo= 'fedora-updates',
    repoUrl= 'http://apt.kde-redhat.org/apt/kde-redhat',
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
