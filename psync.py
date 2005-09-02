#! /usr/bin/python
# (c) 2004
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

# thanks to cholo

import apt_pkg
from os.path import dirname, basename
from os import stat, mkdir, listdir, unlink, rename, system, removedirs
from tempfile import mkdtemp
import sys
from optparse import OptionParser
import gzip

class Psync:
    def __init__ (self, cont=False, consistent=True, limit=20, verbose=False):
        """_attr means readonly
        """
        self._cont= cont
        self._saveSpace= not consistent
        self._limit= limit
        self._verbose= verbose
        self.delete= []
        self.failed= []

    def stat(self, f):
        """ Safe replacement for os.stat() """
        ans = True
        try:
            stat(f)
        except OSError:
            ans = False
        return ans

    def makedirs(self, dirname):
        """ Better replacement for os.makedirs():
            doesn't fails if some intermediate dir already exists.
        """
        # print "making %s" % dirname

        dirs = dirname.split('/')
        i = ''
        while len(dirs):
            i += dirs.pop(0)+'/'
            try:
                mkdir(i)
            except OSError, e:
                # print "%s failed: %s" % (i, e)
                pass

    def grab(self, filename, url, cont=True):
        """ Fetches a file if it does not exist or continues downloading
            a previously partially downloaded file.
        """
        print "%s -> %s" % (url, filename)
        _dir = dirname(filename)
        self.makedirs(_dir)

	# fix cont smantics
	# if file exists and not cont, delete
	if not cont and self.stat (filename):
	    unlink (filename)

        command = "curl -f -C - --limit-rate %sk -o %s %s" % (self._limit, filename, url)

        # Curl has not an equivalent parameter for Wget's -t (number of tries)...
        # Curl returns 0 on successful download, 2 when interrupted by the user
        # with Ctrl-C and 22 when the file was not found.
        # the code 22 is really returned as 22*256==5632 :(
        curlExitCode = 1
        while curlExitCode != 0 and curlExitCode != 2 and curlExitCode != 0x1600:
            curlExitCode = system(command)
            # print "cec= %x" % curlexitcode
	    print

	if curlExitCode==2:
	    raise KeyboardInterrupt

        return curlExitCode

    def checkold(self, _file):
        """ Checks for present files for an older version of this package.
            Also creates the directory just in case it doesn't exist.
        """
        filename = basename(_file)
        (name, version) = filename.split('_')[:2]

        _dir = dirname(_file)
        self.makedirs(_dir)

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
		if self._verbose:
		    print "ignoring %s" % f

        return ans

    def getPackage (self, baseUrl, localDir, fileName, size):
        """ Get one package, making sure it's the right size
            and that old versions will end deleted.
        """
        ans= 0
        url= "%s/%s" % (baseUrl, fileName)
        _file= "%s/%s" % (localDir, fileName)

        old= self.checkold (_file)
        if old:
            if not self._saveSpace:
                for i in old:
                    print "%s: wrong version, deleted" % i
                    unlink (i)
            else:
                if self._verbose:
                    print "%s: wrong version, marked for deletion" % old
                self.delete+= (old)

        try:
            s= stat (_file)
            # print "%d<>%d" % (s.st_size, size)
            if s.st_size!=size:
                if self._verbose:
                    print "%s: wrong size %d" % (_file, s.st_size)
                ans= self.grab (_file, url, cont=True)
            else:
                if self._verbose:
                    print "%s: already here, skipping" % _file

        except OSError:
            if self._verbose:
                print "%s: not here" % _file
            ans= self.grab (_file, url)

        if ans==0x1600:
            self.failed.append ("%s/%s" % (localDir, fileName))

    def main(self, onlyThese=[]):
        apt_pkg.init ()

        config= []
        config+= [{
            'local': 'debian',
            'url': 'http://http.us.debian.org/debian',
            'distro': 'sid',
            'arch': 'i386',
            'modules': [ 'main', 'non-free', 'contrib' ],
        }]
        config+=[{
            'local': 'debian-non-US',
            'url': 'http://non-us.debian.org/debian-non-US',
            'distro': 'sid/non-US',
            'arch': 'i386',
            'modules': [ 'main', 'non-free', 'contrib' ],
        }]

	# deb ftp://ftp.nerim.net/debian-marillat/ unstable main
	config+= [{
	    'local': 'marillat',
	    'url': 'ftp://ftp.nerim.net/debian-marillat',
	    'distro': 'unstable',
	    'arch': 'i386',
	    'modules': [ 'main' ],
	}]

        # ubuntu
        config+= [{
            'local': 'ubuntu',
            'url': 'http://archive.ubuntu.com/ubuntu',
            'distro': 'hoary',
            'arch': 'i386',
            'modules': [ 'main' ],
        }]

        config+= [{
            'local': 'ubuntu-warty',
            'url': 'http://archive.ubuntu.com/ubuntu',
            'distro': 'warty',
            'arch': 'i386',
            'modules': [ 'main', 'restricted', 'universe' ],
        }]

	if onlyThese:
	    distros= [ x for x in config if x['local'] in onlyThese ]
	else:
	    distros= config

        finished= True

        try:
            for conf in distros:
                _local= conf['local']
                baseurl= conf['url']
                distro= conf['distro']
                arch= conf['arch']
                modules= conf['modules']

                if not cont:
                    # create tmp dir
                    _dir= ".tmp"
                    if self._verbose:
                        print "not cont: working on %s" % _dir

                    # skipping Release

                    # Contents
                    _file= "%s/%s/dists/%s/Contents-%s.gz" % (_dir, _local, distro, arch)
                    url= "%s/dists/%s/Contents-%s.gz" % (baseurl, distro, arch)
                    self.grab (_file, url, cont=cont)
                else:
                    _dir= '.'

                # process Packages
                delete= []
                failed= []
                for module in modules:
                    # download the .gz only and process from there
                    packages= "%s/%s/dists/%s/%s/binary-%s/Packages" % (_dir, _local, distro, module, arch)
                    packagesGz= packages+".gz"

                    if not cont or not self.stat (packagesGz):
                        url= "%s/dists/%s/%s/binary-%s/Packages.gz" % (baseurl, distro, module, arch)
                        self.grab (packagesGz, url, cont=cont)

                    if self._verbose:
                        print "opening %s" % packagesGz
                    f= gzip.open (packagesGz)
                    o= open (packages, "w+")

                    # for line in f.xreadlines ():
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

                            self.getPackage (baseurl, _local, filename, size)
                        line= f.readline ()

                # summary of failed pkgs
                if failed:
                    print "====="
                    for i in failed:
                        print i
                    print "----- %d package(s) failed"

                o.close ()
                f.close ()

                # done
                if not cont:
                    # skipping Release

                    # Packages
                    for module in modules:
                        for ext in ('', '.gz'):
                            old= "%s/%s/dists/%s/%s/binary-%s/Packages%s" % (_dir, _local, distro, module, arch, ext)
                            new= "%s/dists/%s/%s/binary-%s/Packages%s" % (_local, distro, module, arch, ext)
                            try:
                                self.makedirs (dirname (new))
                                if self._verbose:
                                    print "moving %s -> %s" % (old, new)
                                unlink (new)
                                rename (old, new)
                            except OSError:
                                # better error report!
                                try:
                                    unlink (old)
                                except OSError:
                                    # was here anyways
                                    pass
                        removedirs (dirname (old))

                    # Contents
                    old= "%s/%s/dists/%s/Contents-%s.gz" % (_dir, _local, distro, arch)
                    new= "%s/dists/%s/Contents-%s.gz" % (_local, distro, arch)
                    self.makedirs (dirname (new))
                    if self._verbose:
                        print "moving %s -> %s" % (old, new)
                    rename (old, new)
                    removedirs (dirname (old))

                if consistent:
                    # they're old anyways
                    for _file in delete:
                        print "unlinking %s" % _file
                        unlink (_file)

        except KeyboardInterrupt:
            finished= False
            # curl stays always in the same line
            print
	except (), e:
	    try:
		print "error prcessing %s" % filename
	    except:
		pass
	    raise e

if __name__=='__main__':
    parser= OptionParser ()
    parser.add_option ('-c', '--continue', dest='c', action='store_true', default=False)
    parser.add_option ('-d', '--distro', dest='d', action='append')
    parser.add_option ('-l', '--limit', dest='l', type='int', default=20)
    parser.add_option ('-q', '--quiet', dest='v', action='store_false', default=False)
    parser.add_option ('-s', '--save-space', dest='t', action='store_false')
    parser.add_option ('-t', '--consistent', dest='t', action='store_true', default=True)
    parser.add_option ('-v', '--verbose', dest='v', action='store_true')
    (opts, args)= parser.parse_args ()

    cont= opts.c
    consistent= opts.t
    limit= opts.l
    verbose= opts.v
    distros= opts.d

    syncer= Psync (cont, consistent, limit, verbose)
    syncer.main (distros)
