# (c) 2006
# Marcos Dione <mdione@grulic.org.ar>

from os.path import dirname
import os
import libxml2
import errno

from psync.core import Psync
from psync.utils import makedirs, grab, symlink

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.Cpan')
logger.setLevel(logLevel)

# "BUG": no support for "long usernames"
# see authors/00.Directory.Is.Not.Maintained.Anymore

# "BUG": no support for calculating checksums (too much cpu?) yet

class Cpan (Psync):
    def __init__ (self, **kwargs):
        super (Cpan, self).__init__ (**kwargs)
        self.checksums= []

    def releaseDatabases (self, download=True):
        yield ('authors/00whois.html', False)
        # yield ('authors/00whois.xml', True)
        yield ('authors/01mailrc.txt.gz', False)
        yield ('authors/02STAMP', False)

        # CHECKSUMS' *are* databases :-|
        # download 00whois.xml and get CHECKSUMS'
        filename= '%(tempDir)s/%(repoDir)s/authors/00whois.xml' % self
        url= '%(repoUrl)s/authors/00whois.xml' % self
        if download:
            found= grab (filename, url, cont=False, progress=self.progress)
            if found!=0:
                raise ProtocolError (proto=url[:url.index (':')].upper (), code=found, url=url)

            whois= libxml2.parseFile(filename).getRootElement()
            whoisChild= whois.children
            while whoisChild:
                if whoisChild.name=='cpanid':
                    dataChild= whoisChild.children
                    while dataChild:
                        if dataChild.name=='id':
                            cpanId= dataChild.content.strip ()
                        if dataChild.name=='type':
                            cpanType= dataChild.content.strip ()
                        dataChild= dataChild.next

                    if cpanType=='author':
                        # authors/id/A/AB/ABIGAIL will be the real dir
                        initial= cpanId[:1]
                        initials= cpanId[:2]
                        chksum= "authors/id/%s/%s/%s/CHECKSUMS" % (initial, initials, cpanId)
                        self.checksums.append (chksum)
                        yield (chksum, False)

                        makedirs ("%s/authors/id/%s/%s/%s" % (self.repoDir, initial, initials, cpanId))
                        # authors/id/A/ABIGAIL and
                        # authors/id/ABIGAIL will be symlinks to
                        # authors/id/A/AB/ABIGAIL
                        # note they're relative ones.
                        symlink ("%s/%s" % (initials, cpanId),
                                 "%s/authors/id/%s/%s" % (self.repoDir, initial, cpanId), self.verbose)
                        symlink ("%s/%s/%s" % (initial, initials, cpanId),
                                 "%s/authors/id/%s" % (self.repoDir, cpanId), self.verbose)

                whoisChild= whoisChild.next
        else:
            for chksum in self.checksums:
                yield (chksum, False)

    def files (self):
        for chkfile in self.checksums:
            try:
                # we *need* a httpStat :-[
                data= self.perlToPython ("%s/%s/%s" % (self.tempDir, self.repoDir, chkfile))
            except IOError, e:
                if e.errno!=2:
                    raise e
                else:
                    logger.warn ('[Ign] %s (%s)' % (chkfile, str (e)))
            else:
                for filename in data.keys ():
                    isdir= data[filename].get ('isdir')
                    if isdir is None or not isdir:
                        yield ("%s/%s" % (dirname (chkfile), filename), data[filename]['size'])
                    else:
                        chksum= "%s/%s/CHECKSUMS" % (dirname (chkfile), filename)
                        # download the CHECKSUM
                        filename= ("%(tempDir)s/%(repoDir)s/" % self)+chksum
                        url= ("%s/%s" % (self.repoUrl, chksum))
                        found= grab (filename, url, cont=False, progress=self.progress)
                        if found!=0:
                            raise ProtocolError (proto=url[:url.index (':')].upper (), code=found, url=url)
                        # add it to checksums
                        # authors/id comes in chkfile path
                        # we're sure this must be there
                        self.checksums.append ( (chksum, True) )

    def finalReleaseDBs (self):
        for (db, critic) in self.releaseDatabases (download=False):
            yield (db, critic)
        yield ('authors/00whois.xml', True)

    def perlToPython (self, chkfile):
        """
        loads a CHECKSUM and returns a dict
        """
        perl= open (chkfile)

        line= perl.readline ()
        while line!='$cksum = {\n':
            line= perl.readline ()
        code= line.replace ('$', '')

        line= perl.readline ()
        while line!='};\n':
            code+= line.replace ('=>', ':')
            line= perl.readline ()
        code+= line.replace (';', '')

        exec code
        return cksum

    def getSubChkSums (self, chkfile):
        data= self.perlToPython (chkfile)
        return [ "%s/%s/CHECKSUMS" % (dirname (chkfile), subdir)
                 for subdir in data.keys ()
                 if data[subdir].get ('isdir')==1 ]

# end
