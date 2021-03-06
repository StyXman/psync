# (c) 2011
# Marcos Dione <mdione@grulic.org.ar>

import sqlalchemy

MEGABYTE= 1048576.0

if sqlalchemy.__version__[:3] in ('0.4', '0.5'):
    from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
    from sqlalchemy.orm import mapper, sessionmaker

    # TODO: echo=True on debug
    engine= create_engine ('sqlite:///status.sqlt')
    metadata= MetaData ()

    table= Table ('status', metadata,
        Column ('id', Integer, primary_key=True),
        Column ('repo', String (20)),
        Column ('distro', String (20)),
        Column ('release', String (20)),
        Column ('arch', String (20)),
        Column ('module', String (20)),
        Column ('lastTried', DateTime),
        Column ('lastSucceeded', DateTime),
        Column ('lastDownloaded', Integer),
        Column ('size', Integer),
        )

    metadata.create_all (engine, checkfirst=True)

    class Status (object):
        def __init__ (self, repo, distro, release, arch, module, lastTried, lastSucceeded, lastDownloaded, size):
            self.repo= repo
            self.distro= distro
            self.release= release
            self.arch= arch
            self.module= module
            self.lastTried= lastTried
            self.lastSucceeded= lastSucceeded
            self.lastDownloaded= lastDownloaded
            self.size= size

    mapper (Status, table)

    Session= sessionmaker (autoflush=True, transactional=True)
    Session.configure (bind=engine)
    session= Session ()

if sqlalchemy.__version__[:3] in ('0.6', '0.7'):
    from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import mapper, sessionmaker

    # TODO: echo=True on debug
    engine= create_engine ('sqlite:///status.sqlt')
    metadata= MetaData ()
    Base = declarative_base()

    class Status (Base):
        __tablename__= 'status'
        
        id=             Column (Integer, primary_key=True)
        repo=           Column (String (20))
        distro=         Column (String (20))
        release=        Column (String (20))
        arch=           Column (String (20))
        module=         Column (String (20))
        lastTried=      Column (DateTime)
        lastSucceeded=  Column (DateTime)
        lastDownloaded= Column (Integer)
        size=           Column (Integer)
        
        def __init__ (self, repo, distro, release, arch, module, lastTried, lastSucceeded, lastDownloaded, size):
            self.repo= repo
            self.distro= distro
            self.release= release
            self.arch= arch
            self.module= module
            self.lastTried= lastTried
            self.lastSucceeded= lastSucceeded
            self.lastDownloaded= lastDownloaded
            self.size= size

    Base.metadata.create_all (engine, checkfirst=True)

    Session = sessionmaker (bind=engine)
    session = Session ()


def getStatus (repo=None, distro=None, release=None, arch=None, module=None, **kwargs):
    status= session.query (Status).filter_by (repo=repo, distro=distro, release=release, arch=arch, module=module).first ()
    if status is None:
        status= Status (repo, distro, release, arch, module, None, None, 0, 0)
        session.add (status)

    return status

def writeStatusFile (status_file, config):
    statusFile= open (status_file, "w+")
    statusFile.write ("<table border=\"1\" cellpadding=\"5%\">\n")
    statusFile.write ("<tr><th>Repository</th><th>Distro</th><th>Release</th><th>Arch</th><th>Modules</th><th>Last Tried</th><th>Last Succeeded</th><th>Size</th><th>Last Update Size</th>\n")

    for repo in config:
        distros= repo.get ('distros', [ None ])
        for distro in distros:
            releases= repo.get ('releases', [ None ])
            for release in releases:
                archs= repo.get ('archs', [ None ])
                for arch in archs:
                    modules= repo.get ('modules', [ None ])
                    if modules==[ None ]:
                        modulesText= "&nbsp;"
                    else:
                        modulesText= ", ".join (modules)

                    size= 0
                    lastDownloaded= 0
                    for module in modules:
                        status= getStatus (repo['repo'], distro, release, arch, module)
                        size+= status.size
                        lastDownloaded+= status.lastDownloaded
                    
                    firstStatus= getStatus (repo['repo'], distro, release, arch, modules[0])
                    lastStatus= getStatus (repo['repo'], distro, release, arch, modules[-1])
                    if firstStatus.lastTried is not None:
                        # TODO: size, last amount downloaded
                        if lastStatus.lastSucceeded is not None:
                            text= ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%7.2f MiB</td><td>%7.2f MiB</td></tr>\n" %
                                (repo['repo'], distro, release, arch, modulesText, firstStatus.lastTried.strftime ("%a %d %b, %H:%M"), lastStatus.lastSucceeded.strftime ("%a %d %b, %H:%M"), size/MEGABYTE, lastDownloaded/MEGABYTE))
                        else:
                            text= ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>&nbsp;</td><td>%7.2f MiB</td><td>%7.2f MiB</td></tr>\n" %
                                (repo['repo'], distro, release, arch, modulesText, firstStatus.lastTried.strftime ("%a %d %b, %H:%M"), size/MEGABYTE, lastDownloaded/MEGABYTE))

                        statusFile.write (text.replace ("None", "&nbsp;"))

    statusFile.write ("</table>\n")
    statusFile.close ()
