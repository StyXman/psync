# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import unlink, removedirs
from os.path import dirname, basename
from traceback import print_exc
import os
import errno

from psync.utils import stat, makedirs, grab, rename

from psync import logLevel
import logging
logger = logging.getLogger('psync.core')
logger.setLevel(logLevel)

class DictException (Exception):
    def __init__ (self, **kwargs):
        self.__dict__.update(kwargs)
        self.args= kwargs

class ProtocolError (DictException):
    pass

class DependencyError (DictException):
    pass

class Psync(object):
    def __init__ (self, verbose=False, **kwargs):
        self.verbose= verbose
        self.__dict__.update(kwargs)
        
        # file tracking
        self.releaseFailed= False # something has failed for the release
        self.failedFiles= [] # files that failed to download
        self.keep= {}
        
        # counters
        self.repoFiles= 0
        # repo, release or arch?
        self.repoSize= 0
        self.downloadedSize= 0

    # simulate to be a dict for suitability to % operator
    def __getitem__ (self, key):
        return getattr (self, key)

    def getPackage (self, filename, size):
        """ Get one package, making sure it's the right size
            and that old versions will end deleted.
            Returns a list of really downloaded files. Could be empty.
        """
        # summary= []
        ans= 0
        
        url= ("%(repoUrl)s/%(baseDir)s/" % self)+filename
        _file= os.path.normpath (("%(repoDir)s/%(baseDir)s/" % self)+filename)

        tempDir = dirname (_file)
        makedirs (tempDir)

        try:
            s= os.stat (_file)
        except OSError:
            # the file does not exist; download it
            # logger.debug ("about to download %s" % _file)
            if not self.dry_run:
                ans= grab (_file, url, limit=self.limit, progress=self.progress)
            if size is None:
                s= os.stat (_file)
                size= s.st_size
                
            self.downloadedSize+= size
            # summary.append (basename(_file))
        else:
            if size is not None and s.st_size!=size:
                # logger.info ("%s: wrong size %d; should be %d" % (_file, s.st_size, size))
                if not self.dry_run:
                    ans= grab (_file, url, limit=self.limit, cont=True, progress=self.progress)
                if size is None:
                    s= os.stat (_file)
                    size= s.st_size
                self.downloadedSize+= size
                # summary.append (basename(_file))
            else:
                if self.verbose:
                    # logger.info ("%s: already here, skipping" % _file)
                    pass
        self.keep[_file]= 1

        if ans==0x1600:
            # only 404 is relevant here
            logger.warn ('failed')
            self.failedFiles.append (_file)
            self.releaseFailed= True
        elif ans==0x02:
            # curl is not here
            raise DependencyError (package='curl')

        # return summary

    def processRepo (self):
        """
        Process the whole repo.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        # summary= []
        if not self.save_space and not self.process_old:
            # create tmp dir
            self.tempDir= ".tmp"
            logger.debug ("not cont: working on %s" % self.tempDir)
        else:
            self.tempDir= '.'

        distros= getattr (self, 'distros', [None])
        for distro in distros:
            # summary.append ("distro: %s" % distro)
            self.distro= distro
            for release in self.releases:
                self.release= release
                # releaseSummary= self.processRelease ()
                self.processRelease ()
        
        # summary of failed pkgs
        if self.failedFiles!=[]:
            logger.warn ("failed packages:")
            for i in self.failedFiles:
                logger.warn (i)
            logger.warn ("----- %d/%d package(s) failed" % (len (self.failedFiles), self.repoFiles))
            # this is gonna be ugly
            # so ugly I sent it to another function
        else:
            # summary+= releaseSummary
            pass

        # clean up
        self.cleanRepo ()

        # return summary
    
    def keepOldFiles (self):
        # force it to use the old databases
        try:
            self.tempDir= '.'
            distros= getattr (self, 'distros', [ None ])
            for distro in distros:
                self.distro= distro
                releases= getattr (self, 'releases', [ None ])
                for release in releases:
                    self.release= release
                    archs= getattr (self, 'archs', [ None ])
                    for arch in archs:
                        self.arch= arch
                        modules= getattr (self, 'modules', [ None ])
                        for module in modules:
                            self.module= module
                            for filename, size in self.files ():
                                filename= os.path.normpath (("%(repoDir)s/%(baseDir)s/" % self)+filename)
                                logger.debug ('keeping %s' % filename)
                                self.keep[filename]= 1
                            databases= self.finalDBs()
                            for (database, critic) in databases:
                                dst= os.path.normpath (("%(repoDir)s/%(baseDir)s/" % self)+database)
                                self.keep[dst]= 1
        except IOError:
            # some database does not exist in the mirror
            # so, wipe'em all anyways
            pass
        
    def processRelease (self):
        """
        Process one release.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        try:
            logger.info ('----- processing %(repo)s/%(distro)s/%(release)s' % self)
            # summary= []
            self.releaseFailed= False
            
            # self.getReleaseDatabases ()
            
            archs= getattr (self, 'archs', [ None ])
            for arch in archs:
                self.arch= arch
                logger.info ('----- processing %(repo)s/%(distro)s/%(release)s/%(arch)s' % self)
                # msg= "architecture %s:" % arch
                # summary.append (msg)
                # summary.append ("~" * len (msg))
                modules= getattr (self, 'modules', [ None ])
                for module in modules:
                    # won't log what module we are processing
                    self.module= module
                    # summary+= self.process ()
                    self.process ()
                    
                # summary.append (("total update: %7.2f MiB" % (self.downloadedSize/1048576.0)).rjust (75))
                # summary.append ('')
                # summary.append ('')
                
                # reset count
                self.downloadedSize= 0
    
        except Exception, e:
            self.releaseFailed= True
            logger.warn ('processing %(repo)s/%(distro)s/%(release)s failed due to' % self)
            logger.warn (e)
            print_exc ()
            if ( self.debugging or
                 (isinstance (e, IOError) and e.errno==errno.ENOSPC) or
                 isinstance (e, KeyboardInterrupt) ):
                # debugging, out of disk space or keyb int
                raise e
            
        if self.releaseFailed:
            self.keepOldReleaseFiles ()
        else:
            # self.updateReleaseDatabases ()
            pass
        
        # return summary

    def keepOldReleaseFiles (self):
        logger.warn ('loading old databases for %(repo)s/%(distro)s/%(release)s' % self)
        # force it to use the old databases
        oldTempDir= self.tempDir
        self.tempDir= '.'
        try:
            archs= getattr (self, 'archs', [ None ])
            for arch in archs:
                self.arch= arch
                modules= getattr (self, 'modules', [ None ])
                for module in modules:
                    self.module= module
                    for filename, size in self.files ():
                        filename= os.path.normpath (("%(repoDir)s/%(baseDir)s/" % self)+filename)
                        self.keep[filename]= 1
                        logger.debug (filename+ ('kept for %(repo)s/%(distro)s/%(release)s' % self))
                    databases= self.finalDBs()
                    for (database, critic) in databases:
                        dst= os.path.normpath (("%(repoDir)s/%(baseDir)s/" % self)+database)
                        self.keep[dst]= 1
        except IOError:
            # some database does not exist in the mirror
            # so, wipe'em all anyways
            pass
        
        self.tempDir= oldTempDir

    def process (self):
        """
        Process one module.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        # summary= []
        try:
            # download databases
            self.baseDir= self.baseDirTemplate % self
            logger.debug ("baseDirTemplate: %s" % self.baseDirTemplate)
            logger.debug ("resulting baseDir: %s" % self.baseDir)
            if not self.process_old:
                self.getDatabases ()
            
            # now files
            for filename, size in self.files ():
                # summary+= self.getPackage (filename, size)
                filename= os.path.normpath (filename)
                self.repoFiles+= 1
                self.getPackage (filename, size)
            
            # yes, there is a BUG here, but it's not that grave.
            # which bug? I don't remember :(
            # databases must be updated at release lever.
            if not self.save_space and not self.dry_run and self.failedFiles==[] and not self.process_old:
                self.updateDatabases ()
            else:
                logger.debug ("save: %s, dry: %s, failed: %s" %
                    (self.save_space, self.dry_run, self.failedFiles))
            
        except Exception, e:
            logger.debug ('processing %s failed due to %s' % (self.repo, e))
            if ( self.debugging or
                 (isinstance (e, IOError) and e.errno==errno.ENOSPC) or
                 isinstance (e, KeyboardInterrupt) or
                 isinstance (e, ProtocolError) ):
                # debugging, out of disk space or keyb int
                print_exc ()
                raise e

        # return summary

    def cleanRepo (self):
        logger.debug ('here comes the janitor')
        ignorePaths= getattr (self, 'ignore', [])
        # add repoDir to all ignored paths
        ignorePaths= [ "%s/%s" % (self.repoDir, i) for i in ignorePaths ]
        logger.debug (ignorePaths)
        
        for (path, dirs, files) in os.walk (self.repoDir):
            ignore= False
            for ignorePath in ignorePaths:
                if path.startswith (ignorePath):
                    logger.debug ('ignoring %s' % path)
                    ignore= True
                
            if not ignore:
                for _file in files:
                    filepath= os.path.join (path, _file)
                    if not self.keep.has_key (filepath):
                        # delete de bastard
                        logger.info ('deleting %s' % filepath)
                        os.unlink (filepath)
                    else:
                        logger.debug ('keeping %s' % filepath)
        logger.debug ('janitor out')
        
    def getDatabases (self):
        """
        Downloads the database from the repo
        """
        # get the databases relative paths
        databases= self.databases ()
        logger.debug (databases)
        for (database, critic) in databases:
            # yes: per design, we don't follow the dry_run option here,
            # but the databases won't be swaped at the end either.
            dababaseFilename= ("%(tempDir)s/%(repoDir)s/%(baseDir)s/" % self)+database
            databaseUrl= ("%(repoUrl)s/%(baseDir)s/" % self)+database
    
            found= grab (dababaseFilename, databaseUrl,
                         limit=self.limit, progress=self.progress, cont=False)
            if found!=0 and critic:
                raise ProtocolError (proto=databaseUrl[:databaseUrl.index (':')].upper (), code=found, url=databaseUrl)

    def updateDatabases (self):
        """
        Move the downloaded databases over the old ones
        """
        logger.info ('----- updating databases for %(repo)s/%(distro)s/%(release)s/%(arch)s/%(module)s' % self)
        # get the databases relative paths
        # these can be more 
        databases= self.finalDBs()
        logger.debug (databases)
        for (database, critic) in databases:
            # logger.debug (self.__dict__)
            dst= os.path.normpath (("%(repoDir)s/%(baseDir)s/" % self)+database)
            src= self.tempDir+'/'+dst
            try:
                makedirs (dirname (dst))
                rename (src, dst, overwrite=True)
                self.keep[dst]= 1
            except OSError, e:
                # better error report!
                if not critic:
                    logger.info ('[Ign] %s (%s)' % (src, str (e)))
                else:
                    raise e
        # removedirs (dirname (old))
# end
