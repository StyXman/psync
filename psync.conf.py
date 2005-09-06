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
    'driver': 'PLF',
    'url': 'http://ftp.club-internet.fr/pub/linux/plf/mandrake/free',
    'distro': '10.2',
    'arch': 'i586',
    'modules': [''],
    'hdlist': 'synthesis.hdlist.cz',
}]

config+= [{
    'local': 'mandrake/updates',
    'driver': 'Mandrake',
    'url': 'http://mirrors.kernel.org/mandrake/Mandrakelinux/official/updates',
    'distro': 'LE2005',
    'arch': 'i586',
    'modules': [ 'RPMS' ],
    'hdlist': 'media_info/synthesis.hdlist.cz',
}]

# ubuntu
config+= [{
    'local': 'ubuntu',
    'url': 'http://archive.ubuntu.com/ubuntu',
    'distro': 'hoary',
    'arch': 'i386',
    'modules': [ 'main' ],
}]

config+= [{
    'local': 'ubuntu-warty',
    'url': 'http://archive.ubuntu.com/ubuntu',
    'distro': 'warty',
    'arch': 'i386',
    'modules': [ 'main', 'restricted', 'universe' ],
}]
