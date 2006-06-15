# (c) 2005
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
from psync.utils import gunzip, grab

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Yum')
logger.setLevel(logLevel)

class Yum (Rpm):
    
    def databases (self):
        ans= []

        # download repomd.xml and take from there
        filename= '%(tempDir)s/%(repoDir)s/%(baseDir)s/repodata/repomd.xml' % self
        grab (filename, '%(repoUrl)s/%(baseDir)s/repodata/repomd.xml' % self, 
	      cont=False, progress=self.progress)
        
        repomd= libxml2.parseFile(filename).getRootElement()
        repomdChild= repomd.children
        while repomdChild:
            if repomdChild.name=='data':
                dataChild= repomdChild.children
                while dataChild:
                    if dataChild.name=='location':
                        ans.append ((dataChild.prop ('href'), True))
    
                    dataChild= dataChild.next
            
            repomdChild= repomdChild.next
        
        return ans

    def files (self):
        # build a parser and use it
        # hack
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
            if ( (self.source and not isDebug) or
                 (self.debug and not isSource) or
                 (self.source and self.debug) or
                 (not isSource and not isDebug) ) and
                (i.nevra[4]==self.arch or i.nevra[4]=='all'):
                # (filename, size)
                yield ( ("%(rpmDir)s/" % self)+i.location['href'],
                        int(i.size['package']) )

    def finalDBs (self):
        finals= self.databases ()
        finals.append (('repodata/repomd.xml', True))
        return finals

# end
