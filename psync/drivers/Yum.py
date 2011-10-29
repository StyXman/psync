# (c) 2005-2011
# Marcos Dione <mdione@grulic.org.ar>


import yum
yumMajVers= yum.__version__.split ('.')[0]
if yumMajVers=='2':
    from yum.mdcache import RepodataParser
else:
    from yum.mdparser import MDParser
    

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
                            cont=False, progress=self.progress, verbose=False)
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
        return ans

    def files (self):
        # build a parser and use it
        # hack
        self.baseDir= self.baseDirTemplate % self
        repodataDir= "%(tempDir)s/%(repoDir)s/%(baseDir)s" % self
        primaryGz= repodataDir+'/'+self.primaries[self.arch]

        if yumMajVers=='2':
            parser= RepodataParser (repodataDir)
            if self.verbose:
                parser.debug= True
            
            primary= primaryGz[:-3]
            logger.debug ("processing database %s" % primaryGz)
            # decompress the gz file
            gunzip (primaryGz, primary)
            
            databank= parser.parseDataFromXml (primary)
            packages= databank.values()
        else:
            packages= MDParser (primaryGz)

        try:
            self.rpmList= listdir ("%(repoDir)s/%(baseDir)s/%(rpmDir)s" % self)
        except OSError:
            self.rpmList= []

        for i in packages:
            if self.verbose and yumMajVers==2:
                # i.dump ()
                pass

            if yumMajVers=='2':
                # nevra= (name, epoch, version, release, arch)
                location= i.location['href']
                size= i.size['package']
                arch= i.nevra[4]

            else:
                location= i['location_href']
                size= i['size_package']
                arch= i['arch']
                # fuck Fedora, the repo says it's i386, but the packages are i686
                if arch=='i686':
                    arch= 'i386'

            if not (arch==self.arch or arch=='noarch') and self.verbose:
                logger.warning ('possible wrong arch '+i.location['href'])

            isDebug= 'debuginfo' in location
            isSource= arch=='src'

            if ( (self.source and not isDebug) or
                 (self.debug and not isSource) or
                 (self.source and self.debug) or
                 (not isSource and not isDebug) ):
                     
                relUrl= ("%(baseDir)s/%(rpmDir)s/" % self)+location
                # logger.debug ("found: %s" % relUrl)
                # (filename, size)
                yield ( relUrl, int(size) )

    def finalReleaseDBs (self, old=False):
        if not old:
            finals= self.releaseDatabases (download=False, includeRepomd=True)
        else:
            tempDir= self.tempDir
            self.tempDir= '.'
            finals= self.releaseDatabases (download=False, includeRepomd=True)
            self.tempDir= tempDir

        logger.debug (finals)
        return finals

# end
