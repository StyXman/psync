# (c) 2006
# Marcos Dione <mdione@grulic.org.ar>

from os import listdir
from os.path import dirname, basename

from psync.core import Psync
from psync.utils import stat

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Slack')
logger.setLevel(logLevel)

class Slack(Psync):
    def __init__ (self, **kwargs):
        super (Slack, self).__init__ (**kwargs)
        # apt_pkg.init ()
        self.firstDatabase= True

    def databases(self):
        ans= []
        if self.firstDatabase:
            ans.append ( ('PACKAGES.TXT', True) )
        ans.append ( (self.module+'/PACKAGES.TXT', True) )
        return ans

    def files(self):
        logger.debug ("opening PACKAGES.TXT")
        packages= "%(tempDir)s/%(repoDir)s/slackware-%(release)s/%(module)s/PACKAGES.TXT" % self
        f= open (packages)

        line= f.readline ()
        while line:
            # grab filename
            if line.startswith ('PACKAGE NAME:'):
                filename= line.split()[-1]

            if line.startswith ('PACKAGE LOCATION:'):
                baseDir= line.split()[-1]
                path= "%s/%s" % (baseDir, filename)
                logger.debug ('found file %s' % path)
                
                yield (path, None)
                yield (path+".asc", None)
                yield (path[:-4]+".txt", None)

            line= f.readline ()
        
        f.close ()
        # self.firstDatabase= True

    def finalDBs (self):
	ans= self.databases ()
        self.firstDatabase= False
        return ans

# end
