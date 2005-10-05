# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

from os import listdir
from os.path import basename, dirname, join
import gzip
import re

from psync.core import Psync

class Urpmi (Psync):
    def __init__ (self, cont=False, consistent=True, limit=20, verbose=False, **kwargs):
        super (Urpmi, self).__init__ (cont, consistent, limit, verbose)
        self.__dict__.update(kwargs)
    
    def databases (self, distro, module, arch):
        varDict= self.__dict__
        self.module= module
        self.arch= arch
        self.distroPath= self.distroSpec % varDict
        self.rpmPath= self.distroPath+'/'+(self.rpmSpec % varDict)
        self.synthesis= self.rpmPath+'/'+(self.hdlist % varDict)
        # if self.verbose:
            # print self.__dict__
        
        # luckly curl manages relative paths correctly
        # synthesis= distro+'/'+module+'/'+self.hdlist
        hdlist= self.synthesis.replace ('synthesis.', '')
        # return [synthesis, hdlist]
        return [ (self.synthesis, True) ]

    def files(self, prefix, distro, module, arch):
        synthesis= "%s/%s" % (prefix, self.synthesis)
        
        if self.verbose:
            print "opening %s" % synthesis
        f= gzip.open (synthesis)

        line= f.readline ()
        while line:
            # @info@gstreamer-xvid-0.8.8-1plf.i586@0@24240@Video
            data= line.split('@')
            if data[1]=='info':
                rpm= data[2]
                print rpm
                rpmArch= rpm.split ('.')[-1]
                print rpm
                if rpmArch==arch or rpmArch=='all':
                    yield (self.rpmPath+'/'+rpm+'.rpm', None)
            
            line= f.readline ()
        
        f.close ()

    def checkold(self, _file):
        """ Checks for present files for an older version of this package.
            Also creates the directory just in case it doesn't exist.
        """
        return []

    def finalDBs (self, distro, module, arch):
        return []
