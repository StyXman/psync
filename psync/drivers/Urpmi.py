# (c) 2005-2006
# Marcos Dione <mdione@grulic.org.ar>

from psync.core import DependencyError
try:
    import rpm
except Exception, e:
    raise DependencyError (package='python-rpm', )

from os import listdir, popen
from os.path import basename, dirname, join
import re
from psync.drivers.Rpm import Rpm

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Urpmi')
logger.setLevel(logLevel)

import pdb

# known BUGs:
# error: Unable to open /usr/lib/rpm/rpmrc for reading: No such file or directory.
# zcat: .tmp/mandrake/updates/LE2005/main_updates/media_info/hdlist.cz: decompression OK, trailing garbage ignored

class Urpmi (Rpm):
    def __init__ (self, **kwargs):
        super (Urpmi, self).__init__ (**kwargs)

    def releaseDatabases (self):
        ans= []

        def moduleFunc (self):
            self.baseDir= self.baseDirTemplate % self
            if hasattr (self, 'hdlistTemplate'):
                self.hdlist= self.hdlistTemplate % self
            hdsplit= (dirname (self.hdlist), basename (self.hdlist))
            synthesis= hdsplit[0]+'/synthesis.'+hdsplit[1]
            md5sum= hdsplit[0]+'/MD5SUM'

            ans.append ( (("%(baseDir)s/" % self)+md5sum, True) )
            ans.append ( (("%(baseDir)s/" % self)+synthesis, True) )
            ans.append ( ("%(baseDir)s/%(hdlist)s" % self, True) )

        self.walkRelease (None, None, moduleFunc)
        return ans

    def files(self):
        self.baseDir= self.baseDirTemplate % self
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
                size= header[1000001]
                if size==[]:
                    # fuck mandriva, first giving the wrong sizes and now simply removing it.
                    size= None
                filedata= (("%(baseDir)s/%(rpmDir)s/" % self)+header[1000000], size)
                logger.debug ("yielding %s [%s, %s]" % (filedata[0], self.baseDir, self.rpmDir))
                yield (filedata)

        pipe.close ()

    finalReleaseDBs= lambda self, *more, **even_more: self.releaseDatabases ()

# end
