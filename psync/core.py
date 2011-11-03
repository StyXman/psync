# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import unlink, removedirs
from os.path import dirname, basename
from traceback import print_exc
from time import sleep
import os
import errno

from psync.utils import stat, makedirs, grab, rename, touch, lockFile, unlockFile, MEGABYTE
from psync import status, utils

from psync import logLevel
import logging
logger = logging.getLogger('psync.core')
logger.setLevel(logLevel)

try:
    TopmostException= BaseException
except NameError:
    TopmostException= Exception

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
        # most distros have a release cleanLevel
        # except debian and probably gentoo
        self.cleanLevel= 'release'

        self.__dict__.update(kwargs)

        # file tracking
        self.releaseFailed= False # something has failed for the release
        self.releaseFailedFiles= [] # files that failed to download for a given release
        self.databasesFailed= False # some operation with the database failed

        self.failedFiles= [] # files that failed to download
        self.keep= {}

        # counters
        self.repoFiles= 0
        self.repoSize= 0
        self.distroSize= 0
        self.releaseSize= 0
        self.archSize= 0
        self.moduleSize= 0
        self.downloadedSize= 0

        # whuu?
        self.size= 0

    # simulate to be a dict for suitability to % operator
    def __getitem__ (self, key):
        return getattr (self, key)

    def getPackage (self, filename, size, reget=False):
        """ Get one package, making sure it's the right size
            and that old versions will end deleted.
            Returns a list of really downloaded files. Could be empty.
        """
        ans= 0
        get= False

        url= ("%(repoUrl)s/" % self)+filename
        _file= os.path.normpath (("%(repoDir)s/" % self)+filename)

        tempDir = dirname (_file)
        makedirs (tempDir)

        # the desition to wether download a file or not is, unfortunately, complex
        try:
            s= os.stat (_file)
        except OSError, e:
            if e.errno==errno.ENOENT:
                # the file does not exist; download it
                get= True
            else:
                # something else, can't decide
                raise e
        else:
            # the file is here
            if size is None:
                # we don't know the size, so we assume that the file is ok
                if self.verbose:
                    # logger.info ("%s: already here, skipping" % _file)
                    pass
            else:
                if reget:
                    if s.st_size!=size:
                        # logger.warn ("%s: size differs, regetting" % _file)
                        os.unlink (_file)
                        get= True
                else:
                    if s.st_size<size:
                        logger.warn ("%s: wrong size %d; should be %d" % (_file, s.st_size, size))
                        get= True
                    elif s.st_size>size:
                        # bigger? it cannot be bigger! reget!
                        logger.warn ("%s: wrong size %d; should be %d." % (_file, s.st_size, size))
                        logger.warn ("bigger means something went wrong. deleting and downloading.")
                        os.unlink (_file)
                        get= True

        if get:
            if not self.dry_run:
                if not self.experiment:
                    ans= grab (_file, url, limit=self.limit, progress=self.progress, reget=reget)
                else:
                    touch (_file, size)
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

        # always keep it
        logger.debug ("keeping %s" % _file)
        self.keep[_file]= '%(repo)s/%(distro)s/%(release)s' % self

        if ans==0x1600:
            # only 404 is relevant here
            logger.warn ('failed')
            self.failedFiles.append (_file)
            self.releaseFailed= True
        elif ans==0x02:
            # curl is not here
            raise DependencyError (package='curl')

    def processRepo (self):
        """
        Process the whole repo.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        logger.info ("=== processing "+self.repo)
        # self.statusFile.write ("<tr class=\"distro\"><td>%s</td></tr>\n" % self.label)
        
        self.totalSize= 0
        notLocked= True
        logger.debug ("clean level: %s" % self.cleanLevel)
        
        if self.cleanLevel=='repo':
            # try to lock
            notLocked= False
            self.lockfile= '%s/lock' % self.repoDir
            logger.debug ("lockfile is %s" % self.lockfile)
            if lockFile (self.lockfile):
                notLocked= True
            logger.debug ("keeping %s" % self.lockfile)
            self.keep[self.lockfile]= '%(repo)s' % self

        if notLocked:
            # we gotta clean the lockfile later
            try:
                if not self.save_space and not self.process_old and not self.wipe:
                    # create tmp dir
                    self.tempDir= ".tmp"
                    logger.debug ("not cont: working on %s" % self.tempDir)
                else:
                    self.tempDir= '.'

                distros= getattr (self, 'distros', [None])
                for distro in distros:
                    self.distroSize= 0
                    self.distro= distro
                    if distro is not None:
                        pass
                    
                    releases= getattr (self, 'releases', [None])
                    for release in releases:
                        self.releaseSize= 0
                        self.release= release
                        self.processRelease ()
                        if self.showSize:
                            # in MiB
                            print u"%(releaseSize)10.2f %(repo)s/%(distro)s/%(release)s" % self
                        self.distroSize+= self.releaseSize
                    if self.showSize:
                        # in MiB
                        print u"%(distroSize)10.2f %(repo)s/%(distro)s" % self
                    self.repoSize+= self.distroSize

                if self.cleanLevel=='repo' and not self.showSize and not self.databasesFailed:
                    self.cleanRepo (self.repoDir)
            except TopmostException, e:
                logger.debug ("repo except'ed! %s" % e)
                if self.cleanLevel=='repo':
                    unlockFile (self.lockfile)
                # reraise
                raise
            else:
                if self.cleanLevel=='repo':
                    unlockFile (self.lockfile)
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
            self.lockfile= '%(repoDir)s/lock-%(distro)s-%(release)s' % self
            logger.debug ("lockfile is %s" % self.lockfile)
            if lockFile (self.lockfile):
                notLocked= True
            logger.debug ("keeping %s" % self.lockfile)
            self.keep[self.lockfile]= '%(repo)s/%(distro)s/%(release)s' % self

        if notLocked:
            # we gotta clean the lockfile later
            try:
                logger.info ('---- processing %(repo)s/%(distro)s/%(release)s' % self)
                self.releaseFailed= False
                self.releaseFailedFiles= []

                if (not self.process_old and not self.wipe) or (self.wipe and self.download_db):
                    self.getReleaseDatabases ()

                if not self.wipe:
                    archs= getattr (self, 'archs', [ None ])
                    for arch in archs:
                        self.arch= arch
                        self.archSize= 0
                        logger.info ('----- processing %(repo)s/%(distro)s/%(release)s/%(arch)s' % self)
                        
                        modules= getattr (self, 'modules', [ None ])
                        for module in modules:
                            # won't log what module we are processing
                            self.module= module
                            self.moduleSize= 0
                            self.processModule ()

                            self.archSize+= self.moduleSize
                            if self.showSize:
                                # in MiB
                                print u"%(moduleSize)10.2f %(repo)s/%(distro)s/%(release)s/%(arch)s/%(module)s" % self

                        if self.showSize:
                            # in MiB
                            print u"%(archSize)10.2f %(repo)s/%(distro)s/%(release)s/%(arch)s" % self
                        self.releaseSize+= self.archSize

                        # reset count
                        self.downloadedSize= 0

            except TopmostException, e:
                # BUG: what happens when a database fails to load?
                self.releaseFailed= True
                if self.cleanLevel=='release':
                    unlockFile (self.lockfile)
                logger.warn ('processing %(repo)s/%(distro)s/%(release)s failed due to' % self)
                logger.warn (e)
                print_exc ()
                if ( (isinstance (e, IOError) and e.errno==errno.ENOSPC) or
                        isinstance (e, KeyboardInterrupt) ):
                    # out of disk space or keyb int
                    raise
            finally:
                # BUG: we don't unlock if something fails!
                if self.cleanLevel=='release':
                    unlockFile (self.lockfile)

                status.session.commit ()

            if self.releaseFailed:
                self.keepOldReleaseFiles ()
            elif self.wipe:
                self.keepOldReleaseFiles ()
            else:
                if not self.save_space and not self.dry_run and not self.process_old and not self.showSize:
                    self.updateReleaseDatabases ()
                # else:
                #     logger.warn ('got no databases to continue!')

            if self.cleanLevel=='release' and not self.databasesFailed:
                if self.distro is not None:
                    self.cleanRepo ('%(repoDir)s/%(distro)s/%(release)s' % self)
                else:
                    self.cleanRepo ('%(repoDir)s/%(release)s' % self)
        else:
            logger.warn ("%(repoDir)s/%(distro)s/%(release)s is being processed by another instance; skipping..." % self)

        if not self.showSize:
            print ""

    def processModule (self):
        """
        Process one module.
        Returns a list of strings with a summary of what was done.
        It is for human consumption.
        """
        moduleStatus= status.getStatus (repo=self.repo, distro=self.distro, release=self.release, arch=self.arch, module=self.module)
        if not self.dry_run: # and not self.experiment:
                moduleStatus.lastTried= utils.now ()
        
        for data in self.files ():
            reget= False
            try:
                filename, size, reget= data
            except ValueError:
                filename, size= data

            filename= os.path.normpath (filename)
            self.repoFiles+= 1
            if not self.showSize:
                self.getPackage (filename, size, reget)

            if size is not None:
                self.moduleSize+= size

        moduleStatus.size= self.moduleSize
        if not self.dry_run: # and not self.experiment:
            moduleStatus.lastSucceeded= utils.now ()


    def walkRelease (self, releaseFunc=None, archFunc=None, moduleFunc=None):
        logger.debug ("walking %(repo)s/%(distro)s/%(release)s" % self)
        if releaseFunc is not None:
            releaseFunc (self)
        archs= getattr (self, 'archs', [ None ])
        for arch in archs:
            self.arch= arch
            logger.debug ("walking %(repo)s/%(distro)s/%(release)s/%(arch)s" % self)
            if archFunc is not None:
                archFunc (self)

            modules= getattr (self, 'modules', [ None ])
            for module in modules:
                self.module= module
                logger.debug ("walking %(repo)s/%(distro)s/%(release)s/%(arch)s/%(module)s" % self)
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
        # force it to use the old databases
        oldTempDir= self.tempDir
        self.tempDir= '.'

        def loadFilesAndDatabases (self):
            logger.warn ('loading old databases for %(repo)s/%(distro)s/%(release)s/%(arch)s/%(module)s' % self)
            for data in self.files ():
                reget= False
                try:
                    filename, size, reget= data
                except ValueError:
                    filename, size= data

                filename= os.path.normpath (("%(repoDir)s/" % self)+filename)
                logger.debug ("keeping %s" % filename)
                self.keep[filename]= '%(repo)s/%(distro)s/%(release)s' % self
                # logger.debug (filename+ (' kept for %(repo)s/%(distro)s/%(release)s' % self))

        try:
            self.walkRelease (moduleFunc=loadFilesAndDatabases)
            # the final ones
            databases= self.finalReleaseDBs (old=True)
            for (database, critic) in databases:
                dst= os.path.normpath (("%(repoDir)s/" % self)+database)
                logger.debug ("keeping %s" % dst)
                self.keep[dst]= '%(repo)s/%(distro)s/%(release)s' % self
        except IOError, e:
            # some database does not exist in the mirror
            # so, wipe'em all anyways
            logger.warn ('could not load database for %(repo)s/%(distro)s/%(release)s/%(arch)s/%(module)s' % self)
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
                logger.debug ("keeping %s" % dst)
                self.keep[dst]= '%(repo)s/%(distro)s/%(release)s' % self
            except OSError, e:
                # better error report!
                if not critic:
                    logger.warn ('[Ign] %s (%s)' % (src, str (e)))
                else:
                    self.databasesFailed= True
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
        logger.debug ('here comes the janitor %s' % cleaningPath)
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
                    if not filepath in self.keep:
                        # delete de bastard
                        logger.info ('deleting %s' % filepath)
                        if not self.dry_run:
                            os.unlink (filepath)
                        if self.debugging:
                            # make it slower so we can stop it in time
                            # when it's destroying a repo
                            sleep (0.1)
                    else:
                        logger.debug ('%s found in keep by %s, keeping' % (filepath, self.keep[filepath]))
        logger.debug ('janitor out')

# end
