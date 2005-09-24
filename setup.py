#!/usr/bin/python

from distutils.core import setup

setup(name='psync',
      version='0.2',
      description="mirror sync'er",
      long_description="""
Psync aims to be a repository mirrorer with this goals:
  * keep the mirror usable while it's updating.
  * be able to handle any kind of repository.
""",
      author='Marcos D. Dione',
      author_email='mdione@grulic.org.ar',
      url='http://plantalta.homelinux.net/~mdione/projects/psync/',
      license='GPL',
      packages=['psync',
                'psync.drivers',
                ],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: Spanish',
                   'Natural Language :: English',
                   'Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Topic :: Internet',
                   ],
      )
