# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# example config file

config= []
config+= [{
    'local': 'debian',
    'driver': 'Debian',
    'url': 'http://http.us.debian.org/debian',
    'distro': 'sid',
    'arch': 'i386',
    'modules': [ 'main', 'non-free', 'contrib' ],
}]
config+=[{
    'local': 'debian-non-US',
    'driver': 'Debian',
    'url': 'http://non-us.debian.org/debian-non-US',
    'distro': 'sid/non-US',
    'arch': 'i386',
    'modules': [ 'main', 'non-free', 'contrib' ],
}]

# deb ftp://ftp.nerim.net/debian-marillat/ unstable main
config+= [{
    'local': 'marillat',
    'driver': 'Debian',
    'url': 'ftp://ftp.nerim.net/debian-marillat',
    'distro': 'unstable',
    'arch': 'i386',
    'modules': [ 'main' ],
}]

config+= [{
    'local': 'plf-free',
    'driver': 'Urpmi',
    'url': 'http://ftp.club-internet.fr/pub/linux/plf/mandrake/free',
    'distro': '10.2',
    'distroSpec': '%(distro)s',
    'rpmSpec': '%(arch)s',
    'arch': 'i586',
    'modules': [''],
    'hdlist': '../synthesis.hdlist.cz',
}]

config+= [{
    'local': 'mandrake',
    'driver': 'Urpmi',
    'url': 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official',
    'distro': '2005',
    'arch': 'i586',
    'distroSpec': '%(distro)s/%(arch)s',
    'rpmSpec': 'media/%(module)s',
    'modules': [ 'main', 'contrib', 'jpackage' ],
    'hdlist': '../media_info/synthesis.hdlist_%(module)s.cz',
}]

config+= [{
    'local': 'mandrake/updates',
    'driver': 'Urpmi',
    'url': 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates',
    'distro': 'LE2005',
    'arch': 'i586',
    'distroSpec': '%(distro)s',
    'rpmSpec': 'main_updates',
    'modules': [ '' ],
    'hdlist': 'media_info/synthesis.hdlist.cz',
}]

# ubuntu
config+= [{
    'local': 'ubuntu-hoary',
    'driver': 'Debian',
    'url': 'http://archive.ubuntu.com/ubuntu',
    'distro': 'hoary',
    'arch': 'i386',
    'modules': [ 'main' ],
}]

config+= [{
    'local': 'ubuntu-security',
    'driver': 'Debian',
    'url': 'http://security.ubuntu.com/ubuntu',
    'distro': 'hoary-security',
    'arch': 'i386',
    'modules': [ 'main' ],
}]

config+= [{
    'local': 'ubuntu-warty',
    'driver': 'Debian',
    'url': 'http://archive.ubuntu.com/ubuntu',
    'distro': 'warty',
    'arch': 'i386',
    'modules': [ 'main', 'restricted', 'universe' ],
}]
