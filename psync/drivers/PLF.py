# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import basename, dirname, join
import gzip
import re

from psync.drivers.Urpmi import Urpmi

class PLF (Urpmi):
    pass
