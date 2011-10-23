# (c) 2011
# Marcos Dione <mdione@grulic.org.ar>

import sqlalchemy

if sqlalchemy.__version__[:3]=='0.4':
    from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
    from sqlalchemy.orm import mapper, sessionmaker

    engine= create_engine ('sqlite:///status.sqlt', echo=True)
    metadata= MetaData ()

    table= Table ('status', metadata,
        Column ('id', Integer, primary_key=True),
        Column ('repo', String (20)),
        Column ('distro', String (20)),
        Column ('release', String (20)),
        Column ('arch', String (20)),
        Column ('module', String (20)),
        Column ('lastTried', DateTime),
        Column ('lastSucceeded', DateTime))

    metadata.create_all (engine, checkfirst=True)

    class Status (object):
        def __init__ (self, repo, distro, release, arch, module, lastTried, lastSucceeded):
            self.repo= repo
            self.distro= distro
            self.release= release
            self.arch= arch
            self.module= module
            self.lastTried= lastTried
            self.lastSucceeded= lastSucceeded

    mapper (Status, table)

    Session= sessionmaker (autoflush=True, transactional=True)
    Session.configure (bind=engine)
    session= Session ()

if sqlalchemy.__version__[:3]=='0.5':
    from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
    from sqlalchemy.orm import mapper, sessionmaker
    
    engine= create_engine ('sqlite:///status.sqlt', echo=True)
    metadata= MetaData ()

    table= Table ('status', metadata,
        Column ('id', Integer, primary_key=True),
        Column ('repo', String (20)),
        Column ('distro', String (20)),
        Column ('release', String (20)),
        Column ('arch', String (20)),
        Column ('module', String (20)),
        Column ('lastTried', DateTime),
        Column ('lastSucceeded', DateTime))

    metadata.create_all (engine, checkfirst=True)

    class Status (object):
        def __init__ (self, repo, distro, release, arch, module, lastTried, lastSucceeded):
            self.repo= repo
            self.distro= distro
            self.release= release
            self.arch= arch
            self.module= module
            self.lastTried= lastTried
            self.lastSucceeded= lastSucceeded

    mapper (Status, table)


# writeStatusFile (status_file):
#     statusFile= open (conf.status_file, "w+")
#     statusFile.write ("<table>\n")
#     statusFile.write ("</table>\n")
#     statusFile.close ()
