# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import dirname, basename
import apt_pkg
import gzip

from psyncpkg.core import Psync
from psyncpkg.utils import stat

from psyncpkg import logLevel
import logging
logger = logging.getLogger('psync.drivers.Debian')
logger.setLevel(logLevel)

class Debian(Psync):
    versionPath= "dists/%s/"
    def __init__ (self, **kwargs):
        super (Debian, self).__init__ (**kwargs)
        apt_pkg.init ()
        self.firstDatabase= True

    def databases(self, version_name, module, arch):
        ans= []
        # skipping Release

        # Contents
        if self.firstDatabase:
            ans.append (("dists/%s/Contents-%s.gz" % (version_name, arch), False))
            self.firstDatabase= False
        
        # download the .gz only and process from there
        packages= "dists/%s/%s/binary-%s/Packages" % (version_name, module, arch)
        packagesGz= packages+".gz"

        if self.save_space or not stat (packagesGz):
            ans.append ((packagesGz, True))
        
        logger.debug (ans)
        return ans

    def files(self, prefix, localBase, version, module, arch):
        packages= "%s/dists/%s/%s/binary-%s/Packages" % (prefix, version, module,
                                                         arch)
        packagesGz= packages+".gz"
        
        logger.debug ("opening %s" % packagesGz)
        f= gzip.open (packagesGz)
        o= open (packages, "w+")

        line= f.readline ()
        while line:
            # print line
            o.write (line)

            # grab filename
            if line.startswith ('Filename'):
                filename= line.split()[1]

            # grab size and process
            if line.startswith ('Size'):
                size= int(line.split()[1])
                yield (filename, size)

            line= f.readline ()
        
        o.close ()
        f.close ()
        self.firstDatabase= True

    def finalDBs (self, version, module, arch):
        ans= []
        # skipping Release

        # Packages
        for ext in ('', '.gz'):
            ans.append (("dists/%s/%s/binary-%s/Packages%s" % (version, module,
                                                              arch, ext), True))

        # Contents
        if self.firstDatabase:
            self.firstDatabase= False
        
            ans.append (("dists/%s/Contents-%s.gz" % (version, arch), False))

        logger.debug (ans)
        return ans

    def checkold(self, path):
        """ Checks for present files for an older version of this package.
            Also creates the directory just in case it doesn't exist.
        """
        _dir= dirname (path)
        filename= basename (path)
        (name, version) = filename.split('_')[:2]
        ans = []

        if self.verbose:
            # print 'processing dir %s for %s %s ' % (_dir, name, version)
            pass
        
        for f in listdir(_dir):
            try:
                (fname, fversion) = f.split('_')[:2]
                if self.verbose:
                    # print fname, fversion
                    pass
                # if it's newer, delete the old one
                if fname == name and apt_pkg.VersionCompare(version, fversion) == 1:
                    ans.append("%s/%s" % (_dir, f))
            except ValueError:
                # unpack list of wrong size
                # could be anything
                # when in doubt, leave alne
                logger.debug ("ignoring %s" % f)

        return ans

# end
