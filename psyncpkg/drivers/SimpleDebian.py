# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import dirname, basename
import gzip

from psyncpkg.core import Psync
from psyncpkg.utils import stat

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.drivers.SimpleDebian')
logger.setLevel(logLevel)

class SimpleDebian(Psync):
    def __init__ (self, **kwargs):
        super (SimpleDebian, self).__init__ (**kwargs)
        apt_pkg.init ()
        self.firstDatabase= True

    def databases(self):
        ans= []
        logger.debug (self.__dict__)
        # skipping Release

        # Contents and Release
        # ans.append (("dists/%(release)s/Contents-%(arch)s.gz" % self, False))
        ans.append ( ("/Release", False) )
        ans.append ( ("/Release.gpg", False) )
        self.firstDatabase= False
        
        # download the .gz only and process from there
        packages= "/Packages"
        packagesGz= packages+".gz"

        if self.save_space or not stat (packagesGz):
            ans.append ( (packagesGz, True) )
        
        return ans

    def files(self):
        # packages= "%(tempDir)s/%(repoDir)s/dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % self
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
                filename= line.split()[1]

            # grab size and process
            if line.startswith ('Size'):
                size= int(line.split()[1])
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
            ans.append (( "/Packages"+ext, True ))

        # Contents
        if self.firstDatabase:
            self.firstDatabase= False
        
            # ans.append (("dists/%(release)s/Contents-%(arch)s.gz" % self, False))

        logger.debug (ans)
        return ans

# end
