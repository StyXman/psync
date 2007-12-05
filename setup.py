#!/usr/bin/env python

# from distutils.core import setup
import kdedistutils

data= dict (
    name='psync',
    version='0.4.0',
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
        'psync',
        'psync.drivers',
        ],
    # scripts= ['psy'],
    # data_files= [('bin', ['psync.py'])],
    application_data = ['psy.py', ('examples', ['psync.conf.py'])],
    executable_links = [('psync','psy.py')],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    kdedistutils.setup(**data)
