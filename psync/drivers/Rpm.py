# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>

from os.path import basename, dirname, join
import re

from psync.core import Psync

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Yum')
logger.setLevel(logLevel)

class Rpm (Psync):
    def __init__ (self, **kwargs):
        super (Rpm, self).__init__ (**kwargs)
        self.rpmList= None

# end
