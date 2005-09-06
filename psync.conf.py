# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# example config file

config= []
config+= [{
    'local': 'debian',
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
    'url': 'ftp://ftp.nerim.net/debian-marillat',
    'distro': 'unstable',
    'arch': 'i386',
    'modules': [ 'main' ],
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
