# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>
# Marcelo "xanthus" Ramos <mramos@adinet.com.uy>

import os
from os import mkdir, unlink, system, utime, strerror
from os.path import dirname
from gzip import GzipFile
import errno

from psync import logLevel
import logging
logger = logging.getLogger('psync.utils')
logger.setLevel(logLevel)

def stat(f):
    """ Safe replacement for os.stat() """
    ans = True
    try:
        os.stat(f)
    except OSError:
        ans = False
    return ans

def makedirs(_dirname):
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
            logger.debug ('make dir %s' % i)

def touch (path):
    """
    Does the same than touch(1).
    """
    if stat (path):
        utime (startStamp, None)
    else:
        f= open (path, 'w+')
        f.close()

def rename (src, dst, overwrite=False):
    logger.info ("move: %s -> %s" % (src, dst))
    # os.rename does not bark when overwriting
    if stat (dst) and not overwrite:
        e= IOError ()
        e.errno= errno.EEXIST
        e.strerror= strerror (errno.EEXIST)
        raise e
        
    try:
        os.rename (src, dst)
    except OSError, e:
        if e.errno==18:
            # [Errno 18] Invalid cross-device link
            # ufa. then copy it, you lazy bastard
            srcFile= open (src)
            dstFile= open (dst, 'w+')

            data= srcFile.read (10240)
            while data!='':
                dstFile.write (data)
                data= srcFile.read (10240)

            srcFile.close ()
            dstFile.close ()
            # bye bye you src man
            unlink (src)
        else:
            raise e

def gunzip (gzFileName, fileName):
    inFile= GzipFile (gzFileName)
    outFile= open (fileName, "w+")

    line= inFile.readline ()
    while line:
        # print line
        outFile.write (line)
        line= inFile.readline ()

    inFile.close ()
    outFile.close ()

def getFile(url, destination):
    file_name = fileFromUrl(url)
    if not os.path.exists(destination):
        try:
            def reporter(block, block_size, total_size):
                left = total_size - block * block_size
                sys.stderr.write('\r')
                sys.stderr.write('Downloading %s: ' % file_name)
                if left > 0: # the estimate is a bit rough, so we fake it a bit
                    sys.stderr.write('%sK left.' % (left/1024))
                else:
                    sys.stderr.write('done.')
 
                # it's possible that this line is shorter than the earlier one,
                # so we need to "erase" any leftovers
                sys.stderr.write(' '*10)
                sys.stderr.write('\b'*10)
 
            urllib.urlretrieve(url, destination, reporter)
            sys.stderr.write('\n')
        except: # bare except is ok, exception re-raised below
            if os.path.exists(destination):
                os.unlink(destination)
            raise
 
def grab(filename, url, limit=0, cont=True, progress=False):
    """ Fetchs a file if it does not exist or continues downloading
        a previously partially downloaded file.
    """
    logger.info ("downloading %s" % filename)
    _dir = dirname(filename)
    makedirs(_dir)

    # fix cont semantics
    contStr= ""
    if cont:
        contStr= "-C -"
    # if file exists and not cont, delete
    if not cont and stat (filename):
        unlink (filename)

    silentStr= "-s"
    if progress:
        silentStr= ""

    limitStr= ""
    if limit>0:
        limitStr= "--limit-rate %dk" % limit

    command = "curl -L -f %s %s %s -o %s %s" % (contStr, limitStr, silentStr, filename, url)

    # Curl has not an equivalent parameter for Wget's -t (number of tries)...
    # Curl returns:
    
    # 0 on successful download,
    # 2 when interrupted by the user with Ctrl-C,

    # these codes are really returned as n*256 :(
    # 18 Partial file. Only a part of the file was transferred.
    # 22 when the file was not found (http error 404)
    # 23 disk full
    # 6 unknown host
    finishCodes= (0, 2, 0x1600, 0x1200, 0x1700, 0x600)
    curlExitCode = 1
    while not curlExitCode in finishCodes:
	logger.debug (command)
        curlExitCode = system(command)
        if curlExitCode==0x2100:
            # 33 The range "command" didn't work.
            command = "curl -L -f %s %s -o %s %s" % (limitStr, silentStr, filename, url)

        logger.debug ("cec= 0x%x" % curlExitCode)

    if curlExitCode==2:
        raise KeyboardInterrupt
    elif curlExitCode==0x1700:
        e= IOError ()
        e.errno= errno.ENOSPC
        e.strerror= strerror (errno.ENOSPC)
        raise e

    return curlExitCode

#end
