# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import unlink, removedirs
from os.path import dirname, basename
import os

from psyncpkg.utils import stat, makedirs, grab, rename

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.core')
logger.setLevel(logLevel)

class Psync(object):
    def __init__ (self, verbose=False, **kwargs):
        self.delete= [] # files for deletion (old package versions)
        self.failed= [] # files taht failed to download
        self.updatedFiles= [] # updated packages
        self.downloadedSize= 0
        self.verbose= verbose
        
        logger.debug (self.__dict__)
        self.__dict__.update(kwargs)
        logger.debug (self.__dict__)

    # simulate to be a dict for suitability to % operator
    def __getitem__ (self, key):
        return getattr (self, key)

    def getPackage (self, filename, size):
        """ Get one package, making sure it's the right size
            and that old versions will end deleted.
        """
        ans= 0
        url= ("%(repoUrl)s/%(baseDir)s/" % self)+filename
        _file= ("%(repoDir)s/%(baseDir)s/" % self)+filename

        tempDir = dirname (_file)
        makedirs (tempDir)

        old= self.checkold (_file)
        if old:
            if self.save_space:
                for i in old:
                    logger.info ("%s: wrong version, deleted" % i)
                    unlink (i)
            else:
                logger.info ("%s: wrong versions, marked for deletion" % old)
                self.delete+= (old)

        try:
            s= os.stat (_file)
            # print "%d<>%d" % (s.st_size, size)
        except OSError:
            logger.info ("%s: not here" % _file)
            if not self.dry_run:
                ans= grab (_file, url, limit=self.limit, progress=self.progress)
            self.downloadedSize+= size
            self.updatedFiles.append (basename(_file))
        else:
            if size is not None and s.st_size!=size:
                logger.info ("%s: wrong size %d; should be %d" % (_file, s.st_size, size))
                if not self.dry_run:
                    ans= grab (_file, url, limit=self.limit, cont=True, progress=self.progress)
                self.downloadedSize+= size
                self.updatedFiles.append (basename(_file))
            else:
                logger.info ("%s: already here, skipping" % _file)

        if ans==0x1600:
            self.failed.append ("%s/%s" % (localDir, fileName))

    def processRepo (self):
        if not self.save_space:
            # create tmp dir
            self.tempDir= ".tmp"
            logger.info ("not cont: working on %s" % self.tempDir)
        else:
            self.tempDir= '.'

        distros= getattr (self, 'distros', None)
        if distros is not None:
            for distro in distros:
                self.distro= distro
                for release in self.releases:
                    self.release= release
                    self.processRelease ()
        else:
            for release in self.releases:
                self.release= release
                self.processRelease ()
            
        # summary of failed pkgs
        if self.failed:
            print "====="
            for i in self.failed:
                print i
            print "----- %d package(s) failed" % len (self.failed)

        # clean up
        if not self.save_space and not self.dry_run:
            # they're old anyways
            for _file in self.delete:
                print "unlinking %s" % _file
                unlink (_file)

    def processRelease (self):
        for arch in self.archs:
            self.arch= arch
            modules= getattr (self, 'modules', None)
            if modules is not None:
                for module in self.modules:
                    self.module= module
                    self.process ()
            else:
                self.process ()

    def process (self):
        # download databases
        self.baseDir= self.baseDirTemplate % self
        logger.debug (self.baseDirTemplate)
        logger.debug (self.baseDir)
        
        databases= self.databases ()
        logger.debug (databases)
        for (database, critic) in databases:
            # yes: per design, we don't follow the dry_run option here,
            # but neither the databases will be swaped at the end.
            dababaseFilename= ("%(tempDir)s/%(repoDir)s/%(baseDir)s/" % self)+database
            databaseUrl= ("%(repoUrl)s/%(baseDir)s/" % self)+database

            found= grab (dababaseFilename, databaseUrl,
                            limit=self.limit, progress=self.progress, cont=False)

        # now files
        for filename, size in self.files ():
            self.getPackage (filename, size)
        
        logger.info ('database rook')
        if not self.save_space and not self.dry_run and self.failed==[]:
            for (database, critic) in self.finalDBs():
                # logger.debug (self.__dict__)
                new= ("%(repoDir)s/%(baseDir)s/" % self)+database
                old= self.tempDir+'/'+new
                try:
                    makedirs (dirname (new))
                    if stat (new):
                        unlink (new)
                    rename (old, new)
                except OSError, e:
                    # better error report!
                    if not critic:
                        logger.info ('[Ign] %s (%s)' % (old, str (e)))
                    else:
                        raise e
            # removedirs (dirname (old))
# end
