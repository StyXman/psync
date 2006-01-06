#!/usr/bin/python

from distutils.core import setup

data= dict (
    name='psync',
    version='0.2.4a',
    description="psync is a distribution mirroring utility with consistency in mind.",
    long_description="""
psync is a mirroring utility. its main goal is to be able to update a  
distribution mirror but keep it as consistent as possible. one of the main  
problems updating a mirror is that if the mirroring process is stopped for any  
reason, the mirror stays inconsistent: either some of the packages in the old  
databases were removed or not all the new packages were downloaded. psync aims  
to fix this. it also aims to support as many distributions as possible. 
""",
    author='Marcos D. Dione',
    author_email='mdione@grulic.org.ar',
    url='http://plantalta.homelinux.net/~mdione/projects/psync/',
    license='GPL',
    packages=[
        'psyncpkg',
        'psyncpkg.drivers',
        ],
    scripts= ['psync.py'],
    # data_files= [('examples', ['psync.conf.py'])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: Spanish',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: Utilities',
        ],
    )
      
if __name__=='__main__':
    setup(**data)
