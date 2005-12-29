# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir, popen
from os.path import basename, dirname, join
import gzip
import re
import rpm

from psyncpkg.drivers.Rpm import Rpm

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.drivers.Urpmi')
logger.setLevel(logLevel)

class Urpmi (Rpm):
    
    def databases (self):
        hdsplit= (dirname (self.hdlist), basename (self.hdlist))
        synthesis= hdsplit[0]+'/synthesis.'+hdsplit[1]
        return [ (synthesis, True), (self.hdlist, True) ]

    def files(self):
        hdlist= "%(tempDir)s/%(repoDir)s/%(baseDir)s/%(hdlist)s" % self
        logger.debug ("opening %s" % hdlist)
        pipe= popen ('zcat %s' % hdlist)

        try:
            self.rpmList= listdir ("%(repoDir)s/%(baseDir)s/%(rpmDir)s" % self)
        except OSError:
            self.rpmList= []

        headerList= rpm.readHeaderListFromFD (pipe.fileno())
        for header in headerList:
            rpmArch= header[rpm.RPMTAG_ARCH]
            if rpmArch==self.arch:
                # 1000000-> rpm file name, 1000001-> rpm file size
                yield (self.rpmDir+'/'+header[1000000], header[1000001])
        
        pipe.close ()

    finalDBs= databases

# end
