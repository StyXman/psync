# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import dirname, basename
# import apt_pkg
import gzip

from psync.core import Psync
from psync.utils import stat

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Debian')
logger.setLevel(logLevel)

class Debian(Psync):
    def __init__ (self, **kwargs):
        super (Debian, self).__init__ (**kwargs)
        # apt_pkg.init ()
        self.firstDatabase= True

    def databases(self):
        ans= []
        # Contents and Release
        if self.firstDatabase:
            ans.append (("dists/%(release)s/Contents-%(arch)s.gz" % self, False))
            ans.append (("dists/%(release)s/Release" % self, False))
            ans.append (("dists/%(release)s/Release.gpg" % self, False))
        
        # download the .gz only and process from there
        packages= "dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % (self)
        packagesGz= packages+".gz"
        release= "dists/%(release)s/%(module)s/binary-%(arch)s/Release" % (self)

        # this should be in core
        if self.save_space or not self.cont:
            ans.append ((packagesGz, True))
            ans.append ((release, False))
        
        return ans

    def files(self):
        packages= "%(tempDir)s/%(repoDir)s/dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % self
        packagesGz= packages+".gz"
        
        logger.debug ("opening %s" % packagesGz)
        f= gzip.open (packagesGz)
        o= open (packages, "w+")

        line= f.readline ()
        while line:
            # print line
            o.write (line)

            # grab filename
            if line.startswith ('Filename'):
                filename= line.split()[1]

            # grab size and process
            if line.startswith ('Size'):
                size= int(line.split()[1])
                logger.debug ('found file %s, size %d' % (filename, size))
                yield (filename, size)

            line= f.readline ()
        
        o.close ()
        f.close ()
        self.firstDatabase= True

    def finalDBs (self):
        ans= []
        # skipping Release

        # Packages
        for ext in ('', '.gz'):
            ans.append (( ("dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % self)+ext, True ))

        # Contents
        if self.firstDatabase:
            ans.append (("dists/%(release)s/Contents-%(arch)s.gz" % self, False))
            self.firstDatabase= False

        logger.debug (ans)
        return ans

# end
