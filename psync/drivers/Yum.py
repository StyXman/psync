# (c) 2005-2006
# Marcos Dione <mdione@grulic.org.ar>

from psync.core import DependencyError
try:
    from yum.mdcache import RepodataParser
except Exception, e:
    raise DependencyError (package='yum', )

from os import listdir
from os.path import basename
import libxml2

from psync.drivers.Rpm import Rpm
from psync.utils import gunzip, grab
from psync.core import ProtocolError

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Yum')
logger.setLevel(logLevel)

class Yum (Rpm):

    def releaseDatabases (self, download=True):
        ans= []

        def moduleFunc (self):
            self.baseDir= self.baseDirTemplate % self
            filename= '%(tempDir)s/%(repoDir)s/%(baseDir)s/repodata/repomd.xml' % self
            url= '%(repoUrl)s/%(baseDir)s/repodata/repomd.xml' % self
            if download:
                # download repomd.xml and take from there
                found= grab (filename, url,
                            cont=False, progress=self.progress)
                if found!=0:
                    raise ProtocolError (proto=url[:url.index (':')].upper (), code=found, url=url)

            repomd= libxml2.parseFile(filename).getRootElement()
            repomdChild= repomd.children
            while repomdChild:
                if repomdChild.name=='data':
                    dataChild= repomdChild.children
                    while dataChild:
                        if dataChild.name=='location':
                            ans.append ( (("%(baseDir)s/" % self)+dataChild.prop ('href'), True) )

                        dataChild= dataChild.next

                repomdChild= repomdChild.next

        self.walkRelease (None, None, moduleFunc)
        return ans

    def files (self):
        # build a parser and use it
        # hack
        self.baseDir= self.baseDirTemplate % self
        repodataDir= "%(tempDir)s/%(repoDir)s/%(baseDir)s/repodata" % self

        self.parser= RepodataParser (repodataDir)
        if self.verbose:
            self.parser.debug= True

        primary= repodataDir+'/primary.xml'
        primaryGz= primary+".gz"
        logger.info ("processing database %s" % primaryGz)
        # decompress the gz file
        gunzip (primaryGz, primary)

        try:
            self.rpmList= listdir ("%(repoDir)s/%(baseDir)s/%(rpmDir)s" % self)
        except OSError:
            self.rpmList= []

        databank= self.parser.parseDataFromXml (primary)
        for i in databank.values():
            if self.verbose:
                # i.dump ()
                pass
            # nevra= (name, epoch, version, release, arch)
            isDebug= 'debuginfo' in i.location['href']
            isSource= i.nevra[4]=='src'
            if ( ( (self.source and not isDebug) or
                   (self.debug and not isSource) or
                   (self.source and self.debug) or
                   (not isSource and not isDebug)
                 ) and (i.nevra[4]==self.arch or i.nevra[4]=='noarch') ):
                relUrl= ("%(baseDir)s/%(rpmDir)s/" % self)+i.location['href']
                # logger.debug ("found: %s" % relUrl)
                # (filename, size)
                yield ( relUrl, int(i.size['package']) )

    def finalReleaseDBs (self):
        finals= self.releaseDatabases (download=False)
        finals.append (('%(baseDir)s/repodata/repomd.xml' % self, True))
        return finals

# end
