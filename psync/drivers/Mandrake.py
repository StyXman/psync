# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import basename, dirname, join
import gzip
import re

from psync.drivers.Urpmi import Urpmi

class Mandrake (Urpmi):
    def files(self, prefix, distro, module, arch):
        for (_file, size) in super (Mandrake, self).files (prefix, distro, module, arch):
            _file= _file.replace(arch, '', 1)
            yield (_file, size)
