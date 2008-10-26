# -*- coding: utf-8 -*-
import os
from os import listdir
from os.path import dirname, basename
import gzip

from psync.drivers.Debian import Debian

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.DebianEdos')
logger.setLevel(logLevel)


class DebianEdos (Debian):
    def __init__ (self, debianRepo=None, debianModules= [], **kwargs):
        super (DebianEdos, self).__init__ (**kwargs)
        self.pkgData= {}
        self.debianRepo= debianRepo
        self.debianModules= debianModules

    def readPackagesGz (self, packagesGz, packages=None, addToRepo=True):
        f= gzip.open (packagesGz)
        logger.debug ("opening %s" % packagesGz)
        if packages is not None:
            o= open (packages, "w+")

        line= f.readline ()
        while line:
            # print line,

            # grab filename
            if line.startswith ('Filename'):
                filename= line.split ()[1]
                package= os.path.basename (filename.split ('_')[0])
                # print package

            # grab size and add it to the package data
            if line.startswith ('Size'):
                size= int(line.split ()[1])
                # logger.debug ('found file %s, size %d' % (filename, size))
                if addToRepo:
                    self.pkgData[package]= (filename, size)

            self.edos_in.write (line)
            if packages is not None:
                o.write (line)

            line= f.readline ()
        f.close ()
        if packages is not None:
            o.close ()


    def files (self):
        packages= "%(tempDir)s/%(repoDir)s/dists/%(release)s/%(module)s/binary-%(arch)s/Packages" % self
        packagesGz= packages+".gz"

        self.edos_in, edos_out= os.popen2 ('/usr/bin/edos-debcheck -successes')
        self.readPackagesGz (packagesGz, packages)

        if self.debianRepo is not None:
            values= self.__dict__.copy ()
            for module in self.debianModules:
                values['module']= module
                packagesGz= "%(debianRepo)s/dists/%(release)s/%(module)s/binary-%(arch)s/Packages.gz" % values
                self.readPackagesGz (packagesGz, addToRepo=False)

        self.edos_in.close ()
        logger.debug ('finished feeding data, processing...')

        line= edos_out.readline ()
        while line:
            line= line.strip ()
            package= line.split ()[0]
            try:
                filename, size= self.pkgData[package]
                logger.debug ('%s: %s [%s:%d]' % (line, package, filename, size))

                yield (filename, size)
            except KeyError:
                pass

            line= edos_out.readline ()

        self.firstDatabase= True

# end
