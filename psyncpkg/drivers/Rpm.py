# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>

from os.path import basename, dirname, join
from rpmUtils.miscutils import compareEVR
import re

from psyncpkg.core import Psync

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.drivers.Yum')
logger.setLevel(logLevel)

class Rpm (Psync):
    def __init__ (self, **kwargs):
        super (Rpm, self).__init__ (**kwargs)
        self.rpmList= None

    def checkold(self, filename):
        """ Checks for present files for an older version of this package.
        """
        filename= basename (filename)
        r= re.compile ("(.*)-(.*)-(.*)\.([^\.]*).rpm")
        g= r.match (filename)
        (nname, nversion, nrelease) = (g.group (0), g.group (1), g.group (2))

        ans = []

        for f in self.rpmList:
            try:
                if f.startswith(nname):
                    g= r.match (filename)
                    (oname, oversion, orelease) = (g.group (0), g.group (1), g.group (2))
                    # if it's newer, delete the old one
                    # check names again: aqbanking-1.0.4beta-2.i386.rpm and aqbanking-devel-1.0.4beta-2.i386.rpm
                    if nname==oname and compareEVR ((0, nversion, nrelease), (0, oversion, orelease)) == 1:
                        ans.append("%s/%s" % (_dir, f))
            except ValueError:
                # unpack list of wrong size
                # could be anything
                # when in doubt, leave alone
                logger.debug ("ignoring %s" % f)

        return ans

