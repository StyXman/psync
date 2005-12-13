# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import dirname
import apt_pkg
import gzip

from psyncpkg.core import Psync
from psyncpkg.utils import stat

class Debian(Psync):
    distroPath= "dists/%s/"
    def __init__ (self, **kwargs):
        super (Debian, self).__init__ (**kwargs)
        apt_pkg.init ()
        self.firstDatabase= True

    def databases(self, distro, module, arch):
        ans= []
        # skipping Release

        # Contents
        if self.firstDatabase:
            ans.append (("dists/%s/Contents-%s.gz" % (distro, arch), False))
            self.firstDatabase= False
        
        # download the .gz only and process from there
        packages= "dists/%s/%s/binary-%s/Packages" % (distro, module, arch)
        packagesGz= packages+".gz"

        if not self.cont or not stat (packagesGz):
            ans.append (("dists/%s/%s/binary-%s/Packages.gz" % (distro, module,
                                                               arch), True))
        
        if self.verbose:
            print ans
        return ans

    def files(self, prefix, distro, module, arch):
        packages= "%s/dists/%s/%s/binary-%s/Packages" % (prefix, distro, module,
                                                         arch)
        packagesGz= packages+".gz"
        
        if self.verbose:
            print "opening %s" % packagesGz
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

    def finalDBs (self, distro, module, arch):
        ans= []
        # skipping Release

        # Packages
        for ext in ('', '.gz'):
            ans.append (("dists/%s/%s/binary-%s/Packages%s" % (distro, module,
                                                              arch, ext), True))

        # Contents
        if self.firstDatabase:
            self.firstDatabase= False
        
            ans.append (("dists/%s/Contents-%s.gz" % (distro, arch), False))

        if self.verbose:
            print ans
        return ans

    def checkold(self, filename):
        """ Checks for present files for an older version of this package.
            Also creates the directory just in case it doesn't exist.
        """
        _dir= dirname (filename)
        (name, version) = filename.split('_')[:2]

        ans = []

        for f in listdir(_dir):
            try:
                (fname, fversion) = f.split('_')[:2]
                # if it's newer, delete the old one
                if fname == name and apt_pkg.VersionCompare(version, fversion) == 1:
                    ans.append("%s/%s" % (_dir, f))
            except ValueError:
                # unpack list of wrong size
                # could be anything
                # when ij doulbt, leave alne
                if self.verbose:
                    print "ignoring %s" % f

        return ans
