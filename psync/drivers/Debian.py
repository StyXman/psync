# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import dirname, basename
import gzip
import bz2 as bzip2

from psync.core import Psync
from psync.utils import stat

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Debian')
logger.setLevel(logLevel)

class Debian(Psync):
    def __init__ (self, **kwargs):
        super (Debian, self).__init__ (**kwargs)

    def releaseDatabases(self):
        ans= []
        def releaseFunc (self):
            ans.append (("dists/%(release)s/Release" % self, False))
            ans.append (("dists/%(release)s/Release.gpg" % self, False))

        def archFunc (self):
            ans.append (("dists/%(release)s/Contents-%(arch)s.gz" % self, False))

        def moduleFunc (self):
            # download the .gz only and process from there
            packages= "dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % (self)
            packagesGz= packages+".gz"
            packagesBz2= packages+".bz2"
            release= "dists/%(release)s/%(module)s/binary-%(arch)s/Release" % (self)
            ans.append ( (packages, True) )
            ans.append ( (packagesGz, True) )
            ans.append ( (packagesBz2, True) )
            ans.append ( (release, False) )

        self.walkRelease (releaseFunc, archFunc, moduleFunc)
        return ans

    def files(self):
        packages= "%(tempDir)s/%(repoDir)s/dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % self
        packagesGz= packages+".gz"
        packagesBz2= packages+".bz2"

        logger.debug ("opening %s" % packagesGz)
        gz= gzip.open (packagesGz)
        # bz2= bzip2.BZ2File (packagesBz2, 'w')
        # o= open (packages, "w+")

        line= gz.readline ()
        while line:
            # print line
            # o.write (line)
            # bz2.write (line)
            
            # grab filename
            if line.startswith ('Filename'):
                filename= line.split()[1]

            # grab size and process
            if line.startswith ('Size'):
                size= int(line.split()[1])
                # logger.debug ('found file %s, size %d' % (filename, size))
                yield (filename, size)

            line= gz.readline ()

        # o.close ()
        gz.close ()
        # bz2.close ()
        self.firstDatabase= True

    def finalReleaseDBs (self):
        ans= self.releaseDatabases ()

        def moduleFunc (self):
            # download the .gz only and process from there
            packages= "dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % (self)
            ans.append ( (packages, True) )
        # self.walkRelease (None, None, moduleFunc)

        return ans

# end
