# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import unlink, removedirs
from os.path import dirname, basename
import os

from psyncpkg.utils import stat, makedirs, grab, rename

class Psync(object):
    def __init__ (self, cont=False, consistent=True, limit=20, verbose=False):
        """_attr means readonly
        """
        self.cont= cont
        self.saveSpace= not consistent
        self.limit= limit
        self.verbose= verbose
        self.delete= []
        self.failed= []

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
            if not self.saveSpace:
                for i in old:
                    print "%s: wrong version, deleted" % i
                    unlink (i)
            else:
                if self.verbose:
                    print "%s: wrong version, marked for deletion" % old
                self.delete+= (old)

        try:
            s= os.stat (_file)
            # print "%d<>%d" % (s.st_size, size)
        except OSError:
            if self.verbose:
                print "%s: not here" % _file
            ans= self.grab (_file, url)
        else:
            if size is not None and s.st_size!=size:
                if self.verbose:
                    print "%s: wrong size %d" % (_file, s.st_size)
                ans= self.grab (_file, url, cont=True)
            else:
                if self.verbose:
                    print "%s: already here, skipping" % _file

        if ans==0x1600:
            self.failed.append ("%s/%s" % (localDir, fileName))

    def processDistro(self, conf):
        local= conf['local']
        baseurl= conf['url']
        distro= conf['distro']
        arch= conf['arch']
        modules= conf['modules']

        if not self.cont:
            # create tmp dir
            _dir= ".tmp/"
            if self.verbose:
                print "not cont: working on %s" % _dir
        else:
            _dir= './'

        # process Packages
        delete= []
        failed= []
        for module in modules:
            # download databases
            for (database, critic) in self.databases (distro, module, arch):
                found= self.grab (_dir+local+'/'+database,
                           baseurl+'/'+database, cont=self.cont)

            # now files
            for filename, size in self.files (_dir+local, distro, module, arch):
                self.getPackage (baseurl, local, filename, size)

        # summary of failed pkgs
        if failed:
            print "====="
            for i in failed:
                print i
            print "----- %d package(s) failed"

        # done
        # clean up/rollover
        if not self.cont:
            for module in modules:
                for (database, critic) in self.finalDBs(distro, module, arch):
                    new= local+"/"+database
                    old= _dir+new
                    try:
                        makedirs (dirname (new), self.verbose)
                        if stat (new):
                            unlink (new)
                        rename (old, new, self.verbose)
                    except OSError, e:
                        # better error report!
                        if not critic:
                            print e, old
                        else:
                            raise e
                # removedirs (dirname (old))

        if not self.saveSpace:
            # they're old anyways
            for _file in delete:
                print "unlinking %s" % _file
                unlink (_file)

    grab= grab
