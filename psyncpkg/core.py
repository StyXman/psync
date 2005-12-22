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
        """_attr means readonly
        """
        self.delete= []
        self.failed= []
        self.updatedFiles= []
        self.downloadedSize= 0
        self.verbose= verbose
        
        logger.debug (self.__dict__)
        self.__dict__.update(kwargs)
        logger.debug (self.__dict__)

    def getPackage (self, baseUrl, localDir, fileName, size):
        """ Get one package, making sure it's the right size
            and that old versions will end deleted.
        """
        ans= 0
        url= "%s/%s" % (baseUrl, fileName)
        _file= "%s/%s" % (localDir, fileName)

        _dir = dirname(_file)
        makedirs(_dir)

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

    def processDistro(self, conf):
        local= conf['local']
        baseurl= conf['url']
        version= conf['version']
        arch= conf['arch']
        modules= conf['modules']

        if not self.save_space:
            # create tmp dir
            _dir= ".tmp/"
            logger.info ("not cont: working on %s" % _dir)
        else:
            _dir= './'

        # process Packages
        delete= []
        failed= []
        files= []
        for module in modules:
            # download databases
            for (database, critic) in self.databases (version, module, arch):
                # yes: per design, we don't follow the dry_run option here,
                # but neither the databases will be swaped at the end.
                found= grab (_dir+local+'/'+database,
                           baseurl+'/'+database, limit=self.limit,
                           progress=self.progress)

            # now files
            for filename, size in self.files (_dir+local, local, version, module, arch):
                self.getPackage (baseurl, local, filename, size)

        # summary of failed pkgs
        if failed:
            print "====="
            for i in failed:
                print i
            print "----- %d package(s) failed"

        # done
        # clean up/rollover
        if not self.save_space and not self.dry_run and self.failed!=[]:
            for module in modules:
                for (database, critic) in self.finalDBs(version, module, arch):
                    new= local+"/"+database
                    old= _dir+new
                    try:
                        makedirs (dirname (new))
                        if stat (new):
                            unlink (new)
                        rename (old, new)
                    except OSError, e:
                        # better error report!
                        if not critic:
                            print '[Ign]', e, old
                        else:
                            raise e
                # removedirs (dirname (old))

        if not self.save_space and not self.dry_run:
            # they're old anyways
            for _file in delete:
                print "unlinking %s" % _file
                unlink (_file)

# end
