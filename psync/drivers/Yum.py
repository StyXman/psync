# (c) 2005-2009
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
    def __init__ (self, *args, **kwargs):
        super (Yum, self).__init__ (*args, **kwargs)
        self.primaries= {}

    def releaseDatabases (self, download=True, includeRepomd=False):
        ans= []

        def moduleFunc (self):
            self.baseDir= self.baseDirTemplate % self
            filename= '%(tempDir)s/%(repoDir)s/%(baseDir)s/repodata/repomd.xml' % self
            url= '%(repoUrl)s/%(baseDir)s/repodata/repomd.xml' % self
            if download:
                # download repomd.xml and take from there
                code= grab (filename, url,
                            cont=False, progress=self.progress)
                if code!=0:
                    raise ProtocolError (proto=url[:url.index (':')].upper (), code=code, url=url)
            if includeRepomd:
                ans.append (('%(baseDir)s/repodata/repomd.xml' % self, True))

            logger.debug ('opening '+filename)
            repomd= libxml2.parseFile(filename).getRootElement()
            repomdChild= repomd.children
            while repomdChild:
                if repomdChild.name=='data':
                    dataChild= repomdChild.children
                    while dataChild:
                        if dataChild.name=='location':
                            # only primary.xml is important
                            filename= dataChild.prop ('href')
                            filepath= ("%(baseDir)s/" % self)+dataChild.prop ('href')
                            if filename.endswith ('primary.xml.gz'):
                                self.primaries[self.arch]= filename
                                logger.debug ("found primary "+filename)
                                ans.append ( (filepath, True) )
                            else:
                                logger.debug ("found other "+filename)
                                ans.append ( (filepath, False) )

                        dataChild= dataChild.next

                repomdChild= repomdChild.next

        self.walkRelease (None, None, moduleFunc)
        # hack until I figure out what to do about it
        # return [ database for database in ans if database ]
        return ans

    def files (self):
        # build a parser and use it
        # hack
        self.baseDir= self.baseDirTemplate % self
        repodataDir= "%(tempDir)s/%(repoDir)s/%(baseDir)s" % self

        self.parser= RepodataParser (repodataDir)
        if self.verbose:
            self.parser.debug= True

        primaryGz= repodataDir+'/'+self.primaries[self.arch]
        primary= primaryGz[:-3]
        logger.debug ("processing database %s" % primaryGz)
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

            if not (i.nevra[4]==self.arch or i.nevra[4]=='noarch'):
                logger.warning ('possible wrong arch '+i.location['href'])

            if ( (self.source and not isDebug) or
                 (self.debug and not isSource) or
                 (self.source and self.debug) or
                 (not isSource and not isDebug) ):
                relUrl= ("%(baseDir)s/%(rpmDir)s/" % self)+i.location['href']
                # logger.debug ("found: %s" % relUrl)
                # (filename, size)
                yield ( relUrl, int(i.size['package']) )

    def finalReleaseDBs (self):
        finals= self.releaseDatabases (download=False, includeRepomd=True)
        # finals.append (('%(baseDir)s/repodata/repomd.xml' % self, True))
        logger.debug (finals)
        return finals

# end
