# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>

from yum.mdcache import RepodataParser
from rpmUtils.miscutils import compareEVR
from os import listdir
from os.path import basename
import re
import libxml2

from psyncpkg.core import Psync
from psyncpkg.utils import gunzip, grab

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.drivers.Yum')
logger.setLevel(logLevel)

class Yum (Psync):
    def __init__ (self, **kwargs):
        super (Yum, self).__init__ (**kwargs)
        self.rpmList= None

    def databases (self):
        ans= []

        # download repomd.xml and take from there
        filename= '%(tempDir)s/%(repoDir)s/%(baseDir)s/repodata/repomd.xml' % self
        grab (filename, '%(repoUrl)s/%(baseDir)s/repodata/repomd.xml' % self)
        
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
        
        logger.debug (ans)
        return ans

    def files (self):
        # build a parser and use it
        # hack
        repodataDir= "%(repoDir)s/%(baseDir)s/repodata" % self
        ans= []

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
            if ( (self.source and i.nevra[4]=='src') or
                 (self.debug and i.location['href'].startswith ('debug')) or
                 (not i.nevra[4]=='src') and not i.location['href'].startswith ('debug') ):
                # (filename, size)
                ans.append (( ("%(rpmDir)s/" % self)+i.location['href'],
                             int(i.size['package']) ))

        ans.sort()
        return ans

    def checkold(self, filename):
        """ Checks for present files for an older version of this package.
        """
        filename= basename (filename)
        r= re.compile ("(.*)-(.*)-(.*)\.([^\.]*).rpm")
        g= r.match (filename)
        (nname, nversion, nrelease) = (g.group (0), g.group (1), g.group (2))

        ans = []

        for f in self.rpmList:
            try:
                if f.startswith(nname):
                    g= r.match (filename)
                    (oname, oversion, orelease) = (g.group (0), g.group (1), g.group (2))
                    # if it's newer, delete the old one
                    # check names again: aqbanking-1.0.4beta-2.i386.rpm and aqbanking-devel-1.0.4beta-2.i386.rpm
                    if nname==oname and compareEVR ((0, nversion, nrelease), (0, oversion, orelease)) == 1:
                        ans.append("%s/%s" % (_dir, f))
            except ValueError:
                # unpack list of wrong size
                # could be anything
                # when in doubt, leave alone
                logger.debug ("ignoring %s" % f)

        return ans

    def finalDBs (self):
        finals= self.databases ()
        finals.append (('repodata/repomd.xml', True))
        return finals

# end
