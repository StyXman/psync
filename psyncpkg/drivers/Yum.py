# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>

from yum.mdcache import RepodataParser
from rpmUtils.miscutils import compareEVR
from os import listdir
from os.path import basename
import re

from psyncpkg.core import Psync
from psyncpkg.utils import gunzip

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.drivers.Yum')
logger.setLevel(logLevel)

class Yum (Psync):
    def __init__ (self, **kwargs):
        super (Yum, self).__init__ (**kwargs)
        self.rpmList= None

    def databases (self, version, module, arch):
        baseDir= self.baseDir % locals ()
        ans= []

        # actually, it should download repomd.xml and take from there
        for i in ('repomd.xml', 'comps.xml',
                  'filelists.xml.gz', 'other.xml.gz', 'primary.xml.gz'):
            ans.append (('%s/repodata/%s' % (baseDir, i), True))
        logger.debug (ans)
        return ans

    def files (self, prefix, localBase, version, module, arch):
        ans= []
        # build a parser and use it
        baseDir= self.baseDir % locals ()
        repodataDir= prefix+"/"+baseDir+"/repodata"

        self.parser= RepodataParser (repodataDir)
        if self.verbose:
            self.parser.debug= True

        primary= repodataDir+'/primary.xml'
        primaryGz= primary+".gz"
        logger.info ("processing database %s" % primaryGz)
        # decompress the gz file
        gunzip (primaryGz, primary)

        try:
            self.rpmList= listdir("%s/%s/%s" % (localBase, baseDir, self.rpmDir))
        except OSError:
            self.rpmList= []

        databank= self.parser.parseDataFromXml (primary)
        for i in databank.values():
            if self.verbose:
                # i.dump ()
                pass
            # (filename, size)
            if i.nevra[4]!='src' and not i.location['href'].startswith ('debug'):
                # nevra= (name, epoch, version, release, arch)
                # ans.append (("%s/%s/%s-%s-%s.%s.rpm" % (baseDir, self.rpmDir, i.nevra[0], i.nevra[2], i.nevra[3], i.nevra[4]), i.size['package']))
                ans.append (("%s/%s/%s" % (baseDir, self.rpmDir, i.location['href']), int(i.size['package'])))

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

    def finalDBs (self, version_name, module, arch):
        return self.databases (version_name, module, arch)

# end
