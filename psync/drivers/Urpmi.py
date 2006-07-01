# (c) 2005-2006
# Marcos Dione <mdione@grulic.org.ar>

from psync.core import DependencyError
try:
    import rpm
except Exception, e:
    raise DependencyError (package='python-rpm', )

from os import listdir, popen
from os.path import basename, dirname, join
import gzip
import re
from psync.drivers.Rpm import Rpm

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Urpmi')
logger.setLevel(logLevel)

# known BUG:
# error: Unable to open /usr/lib/rpm/rpmrc for reading: No such file or directory.
# zcat: .tmp/mandrake/updates/LE2005/main_updates/media_info/hdlist.cz: decompression OK, trailing garbage ignored

class Urpmi (Rpm):
    def __init__ (self, **kwargs):
        super (Urpmi, self).__init__ (**kwargs)
        # this flag is for downloading the databases just once
        # self.first= None
    
    def databases (self):
        # logger.debug ("%s, %s" % (self.first, self.release))
        # if self.first==self.release:
            # databases already dowloaded and updated
            # self.tempDir= '.'
            # ans= []
        # else:
        if True:
            # self.first= self.release
            if hasattr (self, 'hdlistTemplate'):
                self.hdlist= self.hdlistTemplate % self
            hdsplit= (dirname (self.hdlist), basename (self.hdlist))
            synthesis= hdsplit[0]+'/synthesis.'+hdsplit[1]
            ans= [ (synthesis, True), (self.hdlist, True) ]
        return ans

    def files(self):
        if hasattr (self, 'hdlistTemplate'):
            self.hdlist= self.hdlistTemplate % self
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
            # logger.debug ("rpm %s arch: %s" % (header[1000000], rpmArch))
            if rpmArch==self.arch or rpmArch=='noarch':
                # 1000000-> rpm file name, 1000001-> rpm file size
                yield (self.rpmDir+'/'+header[1000000], header[1000001])
        
        pipe.close ()

    def finalDBs (self):
        if hasattr (self, 'hdlistTemplate'):
            self.hdlist= self.hdlistTemplate % self
        hdsplit= (dirname (self.hdlist), basename (self.hdlist))
        synthesis= hdsplit[0]+'/synthesis.'+hdsplit[1]
        return [ (synthesis, True), (self.hdlist, True) ]

    # finalDBs= databases
    
# end
