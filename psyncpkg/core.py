# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import unlink, removedirs
from os.path import dirname, basename
import os
import errno

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
            Returns a list of really downloaded files. Could be empty.
        """
        summary= []
        ans= 0
        url= ("%(repoUrl)s/%(baseDir)s/" % self)+filename
        _file= ("%(repoDir)s/%(baseDir)s/" % self)+filename

        tempDir = dirname (_file)
        makedirs (tempDir)

        old= self.checkold (_file)
        if old:
            if self.save_space:
                for i in old:
                    if self.verbose:
                        logger.info ("%s: wrong version, deleted" % i)
                    unlink (i)
            else:
                if self.verbose:
                    logger.info ("%s: wrong versions, marked for deletion" % old)
                self.delete+= (old)

        try:
            s= os.stat (_file)
            # print "%d<>%d" % (s.st_size, size)
        except OSError:
            logger.info ("%s" % _file)
            if not self.dry_run:
                ans= grab (_file, url, limit=self.limit, progress=self.progress)
            self.downloadedSize+= size
            summary.append (basename(_file))
        else:
            if size is not None and s.st_size!=size:
                logger.info ("%s: wrong size %d; should be %d" % (_file, s.st_size, size))
                if not self.dry_run:
                    ans= grab (_file, url, limit=self.limit, cont=True, progress=self.progress)
                self.downloadedSize+= size
                summary.append (basename(_file))
            else:
                if self.verbose:
                    logger.info ("%s: already here, skipping" % _file)

        if ans==0x1600:
            self.failed.append ("%s/%s" % (localDir, fileName))

        return summary

    def processRepo (self):
        """
        Process the whole repo.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        summary= []
        if not self.save_space:
            # create tmp dir
            self.tempDir= ".tmp"
            logger.info ("not cont: working on %s" % self.tempDir)
        else:
            self.tempDir= '.'

        distros= getattr (self, 'distros', None)
        if distros is not None:
            for distro in distros:
                ans.append ("distro: %s" % distro)
                self.distro= distro
                for release in self.releases:
                    self.release= release
                    releaseSummary= self.processRelease ()
        else:
            for release in self.releases:
                self.release= release
                releaseSummary= self.processRelease ()
            
        # summary of failed pkgs
        if self.failed:
            logger.info ("failed packages:")
            for i in self.failed:
                logger.info (i)
            logger.info ("----- %d package(s) failed" % len (self.failed))
        else:
            summary+= releaseSummary

        # clean up
        if not self.save_space and not self.dry_run:
            # they're old anyways
            for _file in self.delete:
                if self.verbose:
                    logger.info ("unlinking %s" % _file)
                unlink (_file)

        return summary

    def processRelease (self):
        """
        Process one release.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        summary= []
        for arch in self.archs:
            self.arch= arch
            msg= "architecture %s:" % arch
            summary.append (msg)
            summary.append ("~" * len (msg))
            modules= getattr (self, 'modules', None)
            if modules is not None:
                for module in self.modules:
                    # won't log what module we are processing
                    self.module= module
                    summary+= self.process ()
            else:
                summary+= self.process ()
            summary.append ("                                total update: %7.2f MiB" %
                (self.downloadedSize/1048576.0))
            summary.append ('')
            summary.append ('')
            # reset count
            self.downloadedSize= 0

        return summary

    def process (self):
        """
        Process one module.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        summary= []
        try:
            # download databases
            self.baseDir= self.baseDirTemplate % self
            logger.debug ("baseDirTemplate: %s" % self.baseDirTemplate)
            logger.debug ("resulting baseDir: %s" % self.baseDir)
            
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
                summary+= self.getPackage (filename, size)
            
            if not self.save_space and not self.dry_run and self.failed==[]:
                self.updateDatabases ()
        except Exception, e:
            logger.info ('processing %s failed due to %s' % (self.repo, e))
            if ( self.debug or
                 (isinstance (e, IOError) and e.errno==errno.ENOSPC) or
                 isinstance (e, KeyboardInterrupt) ):
                # debugging, out of disk space or keyb int
                raise e

        return summary

    def updateDatabases (self):
        if self.verbose:
            logger.info ('updating databases')
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
