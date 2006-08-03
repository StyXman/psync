# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import dirname, basename
import gzip

from psync.core import Psync
from psync.utils import stat

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.SimpleDebian')
logger.setLevel(logLevel)

class SimpleDebian(Psync):
    def __init__ (self, **kwargs):
        super (SimpleDebian, self).__init__ (**kwargs)

    def releaseDatabases(self):
        ans= []
        def moduleFunc (self):
            if getattr (self, 'baseDirTemplate', None) is not None:
                logger.debug ("baseDirTemplate: %s" % self.baseDirTemplate)
                self.baseDir= self.baseDirTemplate % self
            # Contents and Release
            # ans.append (("dists/%(release)s/Contents-%(arch)s.gz" % self, False))
            ans.append ( ("%(baseDir)s/Release" % self, False) )
            ans.append ( ("%(baseDir)s/Release.gpg" % self, False) )

            # download the .gz only and process from there
            packages= "%(baseDir)s/Packages"  % self
            packagesGz= packages+".gz"
            ans.append ( (packagesGz, False) )

        self.walkRelease (None, None, moduleFunc)
        return ans

    def files(self):
        packages= ("%(tempDir)s/%(repoDir)s/" % self)+self.baseDir+"/Packages"
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
                filename= ("%(baseDir)s/" % self)+line.split()[1]

            # grab size and process
            if line.startswith ('Size'):
                size= int(line.split()[1])
                yield (filename, size)

            line= f.readline ()

        o.close ()
        f.close ()
        self.firstDatabase= True

    def finalReleaseDBs (self):
        ans= self.releaseDatabases ()

        def moduleFunc (self):
            # download the .gz only and process from there
            packages= "dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % (self)
            ans.append ( (packages, True) )
        self.walkRelease (None, None, moduleFunc)

        return ans

# end
