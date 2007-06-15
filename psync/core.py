# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import unlink, removedirs
from os.path import dirname, basename
from traceback import print_exc
from time import sleep
import os
import errno

from psync.utils import stat, makedirs, grab, rename, touch, lockFile, unlockFile

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
        
        # defaults
        self.cleanLevel= 'release'
        
        self.__dict__.update(kwargs)

        # file tracking
        self.releaseFailed= False # something has failed for the release
        self.releaseFailedFiles= [] # files that failed to download for a given release

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
        get= False

        url= ("%(repoUrl)s/" % self)+filename
        _file= os.path.normpath (("%(repoDir)s/" % self)+filename)

        tempDir = dirname (_file)
        makedirs (tempDir)

        # logger.debug ('getPackage: asked for %s' % _file)
        try:
            s= os.stat (_file)
        except OSError, e:
            if e.errno==errno.ENOENT:
                # the file does not exist; download it
                # logger.debug ("about to download %s" % _file)
                get= True
            else:
                raise e
        else:
            if size is not None:
                if s.st_size<size:
                    logger.warn ("%s: wrong size %d; should be %d" % (_file, s.st_size, size))
                    get= True
                elif s.st_size>size:
                    # bigger? how's bigger? reget!
                    logger.warn ("%s: wrong size %d; should be %d." % (_file, s.st_size, size))
                    logger.warn ("bigger means something went wrong. deleting and downloading.")
                    os.unlink (_file)
                    get= True
            else:
                if self.verbose:
                    # logger.info ("%s: already here, skipping" % _file)
                    pass

        if get:
            if not self.dry_run:
                if not self.experiment:
                    ans= grab (_file, url, limit=self.limit, progress=self.progress)
                else:
                    touch (_file)
                    ans= 0
            if size is None:
                try:
                    s= os.stat (_file)
                except OSError, e:
                    if e.errno==errno.ENOENT:
                        size= 0
                else:
                    size= s.st_size
            else:
                size= 0

            self.downloadedSize+= size
            # summary.append (basename(_file))

        # always keep it
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
        logger.info ("=== processing "+repo['repo'])
        self.totalSize= 0
        notLocked= True
        logger.debug ("clean level: %s" % self.cleanLevel)
        if self.cleanLevel=='repo':
            # try to lock
            notLocked= False
            lockfile= '%s/lock' % self.repoDir
            logger.debug ("lockfile is %s" % lockfile)
            if lockFile (lockfile):
                notLocked= True
        
        if notLocked:
            # we gotta clean the lockfile later
            try:
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
                    releases= getattr (self, 'releases', [None])
                    for release in releases:
                        self.release= release
                        # releaseSummary= self.processRelease ()
                        self.processRelease ()

                if self.cleanLevel=='repo':
                    self.cleanRepo (self.repoDir)
            except Exception, e:
                if self.cleanLevel=='repo':
                    unlockFile (lockfile)
                # reraise
                raise e
            else:
                if self.cleanLevel=='repo':
                    unlockFile (lockfile)
        else:
            logger.warn ("repo %s is being processed by another instance; skipping..." % self.repo)

        # return summary

    def processRelease (self):
        """
        Process one release.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        notLocked= True
        if self.cleanLevel=='release':
            notLocked= False
            # try to lock
            lockfile= '%(repoDir)s/lock-%(distro)s-%(release)s' % self
            logger.debug ("lockfile is %s" % lockfile)
            if lockFile (lockfile):
                notLocked= True
        
        if notLocked:
            # we gotta clean the lockfile later
            try:
                logger.info ('---- processing %(repo)s/%(distro)s/%(release)s' % self)
                # summary= []
                self.releaseFailed= False
                self.releaseFailedFiles= []

                if not self.process_old:
                    self.getReleaseDatabases ()

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

            except (Exception, KeyboardInterrupt), e:
                # BUG: what happens when a database fails to load?
                self.releaseFailed= True
                if self.cleanLevel=='release':
                    unlockFile (lockfile)
                logger.warn ('processing %(repo)s/%(distro)s/%(release)s failed due to' % self)
                logger.warn (e)
                print_exc ()
                if ( (isinstance (e, IOError) and e.errno==errno.ENOSPC) or
                     isinstance (e, KeyboardInterrupt) ):
                    # out of disk space or keyb int
                    raise e
            else:
                if self.cleanLevel=='release':
                    unlockFile (lockfile)

            if self.releaseFailed:
                self.keepOldReleaseFiles ()
            else:
                if not self.save_space and not self.dry_run and not self.process_old and not self.size:
                    self.updateReleaseDatabases ()
            
            if self.cleanLevel=='release':
                self.cleanRepo ('%(repoDir)s/%(distro)s/%(release)s' % self)
        else:
            logger.warn ("%(repo)s/%(distro)s/%(release)s is being processed by another instance; skipping..." % self)
            
        print ""

        # return summary

    def process (self):
        """
        Process one module.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        # summary= []
        for filename, size in self.files ():
            # summary+= self.getPackage (filename, size)
            filename= os.path.normpath (filename)
            self.repoFiles+= 1
            if not self.size:
                self.getPackage (filename, size)
            else:
                self.totalSize+= size

        # return summary

    def walkRelease (self, releaseFunc=None, archFunc=None, moduleFunc=None):
        if releaseFunc is not None:
            releaseFunc (self)
        archs= getattr (self, 'archs', [ None ])
        for arch in archs:
            self.arch= arch
            if archFunc is not None:
                archFunc (self)

            modules= getattr (self, 'modules', [ None ])
            for module in modules:
                self.module= module
                if moduleFunc is not None:
                    moduleFunc (self)

    def getReleaseDatabases (self):
        """
        Downloads the database for the whole release
        """
        # get the databases relative paths
        databases= self.releaseDatabases ()
        logger.debug (databases)
        logger.info ('------ getting databases for %(repo)s/%(distro)s/%(release)s' % self)
        for (database, critic) in databases:
            # yes: per design, we don't follow the dry_run option here,
            # but the databases won't be swapped at the end either.
            dababaseFilename= ("%(tempDir)s/%(repoDir)s/" % self)+database
            databaseUrl= ("%(repoUrl)s/" % self)+database

            found= grab (dababaseFilename, databaseUrl,
                         limit=self.limit, progress=self.progress, cont=False, verbose=False)
            logger.debug ("%s grabbed" % dababaseFilename)
            if found!=0 and critic:
                raise ProtocolError (proto=databaseUrl[:databaseUrl.index (':')].upper (), code=found, url=databaseUrl)

    def keepOldReleaseFiles (self):
        logger.warn ('loading old databases for %(repo)s/%(distro)s/%(release)s' % self)
        # force it to use the old databases
        oldTempDir= self.tempDir
        self.tempDir= '.'

        def loadFilesAndDatabases (self):
            for filename, size in self.files ():
                filename= os.path.normpath (("%(repoDir)s/" % self)+filename)
                self.keep[filename]= 1
                logger.debug (filename+ (' kept for %(repo)s/%(distro)s/%(release)s' % self))
            # the final ones
            databases= self.finalReleaseDBs ()
            for (database, critic) in databases:
                dst= os.path.normpath (("%(repoDir)s/" % self)+database)
                self.keep[dst]= 1

        try:
            self.walkRelease (moduleFunc=loadFilesAndDatabases)
        except IOError, e:
            # some database does not exist in the mirror
            # so, wipe'em all anyways
            logger.warn ('could not load database for %(repo)s/%(distro)s/%(release)s/%(arch)s/%(modules)s' % self)
            logger.warn (e)

        self.tempDir= oldTempDir

    def updateReleaseDatabases (self):
        """
        Move the downloaded databases over the old ones for the whole release
        """
        logger.info ('------ updating databases for %(repo)s/%(distro)s/%(release)s' % self)
        # get the databases relative paths
        # these can be more
        databases= self.finalReleaseDBs ()
        logger.debug (databases)
        for (database, critic) in databases:
            # logger.debug (self.__dict__)
            dst= os.path.normpath (("%(repoDir)s/" % self)+database)
            src= self.tempDir+'/'+dst
            try:
                makedirs (dirname (dst))
                rename (src, dst, overwrite=True, verbose=self.verbose)
                self.keep[dst]= 1
            except OSError, e:
                # better error report!
                if not critic:
                    logger.warn ('[Ign] %s (%s)' % (src, str (e)))
                else:
                    raise e
        # removedirs (dirname (old))

    def cleanRepo (self, cleaningPath):
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
        logger.debug ('here comes the janitor')
        ignorePaths= getattr (self, 'ignore', [])
        # add cleaningPath to all ignored paths
        ignorePaths= [ "%s/%s" % (cleaningPath, i) for i in ignorePaths ]
        logger.debug (ignorePaths)

        for (path, dirs, files) in os.walk (cleaningPath):
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
                        if self.debugging:
                            # make it slower so we can stop it in time
                            # when it's destroying a repo
                            sleep (0.1)
                    else:
                        logger.debug ('keeping %s' % filepath)
        logger.debug ('janitor out')

# end
