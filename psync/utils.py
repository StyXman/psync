# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

import os
from os import mkdir, unlink, system, utime
from os.path import dirname

def stat(f):
    """ Safe replacement for os.stat() """
    ans = True
    try:
        os.stat(f)
    except OSError:
        ans = False
    return ans

def makedirs(_dirname, verbose=False):
    """ Better replacement for os.makedirs():
        doesn't fails if some intermediate dir already exists.
    """
    # print "making %s" % dirname

    dirs = _dirname.split('/')
    i = ''
    while len(dirs):
        i += dirs.pop(0)+'/'
        try:
            mkdir(i)
        except OSError, e:
            # print "%s failed: %s" % (i, e)
            pass
	else:
	    if verbose:
		print 'make dir %s' % i

def grab(self, filename, url, cont=True):
    """ Fetches a file if it does not exist or continues downloading
        a previously partially downloaded file.
    """
    print "%s -> %s" % (url, filename)
    _dir = dirname(filename)
    makedirs(_dir)

    # fix cont smantics
    # if file exists and not cont, delete
    if not cont and stat (filename):
        unlink (filename)

    command = "curl -L -f -C - --limit-rate %sk -o %s %s" % (self.limit, filename, url)

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

def touch (path):
    """
    Does the same than touch(1).
    """
    if stat (path):
        utime (startStamp, None)
    else:
        f= open (path, 'w+')
        f.close()

def rename (old, new):
    try:
        os.rename (old, new)
    except OSError, e:
        if e.errno==18:
            # [Errno 18] Invalid cross-device link
            # ufa, then copy it, lazy bastard
            oldFile= open (old)
            newFile= open (new, 'w+')
            
            data= oldFile.read (10240)
            while data!='':
                newFile.write (data)
                data= oldFile.read (10240)

            oldFile.close ()
            newFile.close ()
        else:
            raise e