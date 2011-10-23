# (c) 2011
# Marcos Dione <mdione@grulic.org.ar>

import sqlalchemy

if sqlalchemy.__version__[:3]=='0.4':
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

    Session = sessionmaker (bind=engine)
    session = Session ()


def getStatus (repo=None, distro=None, release=None, arch=None, module=None, **kwargs):
    status= session.query (Status).filter_by (repo=repo, distro=distro, release=release, arch=arch, module=module).first ()
    if status is None:
        status= Status (repo, distro, release, arch, module, None, None)
        session.add (status)

    return status

def writeStatusFile (status_file, config):
    statusFile= open (status_file, "w+")
    statusFile.write ("<table>\n")
    statusFile.write ("<tr><th>Repository</th><th>Distro</th><th>Release</th><th>Arch</th><th>Module</th><th>Last Tried</th><th>Last Succeeded</th></tr>\n")
    
    for repo in config:
        distros= repo.get ('distros', [ None ])
        for distro in distros:
            releases= repo.get ('releases', [ None ])
            for release in releases:
                archs= repo.get ('archs', [ None ])
                for arch in archs:
                    modules= repo.get ('modules', [ None ])
                    for module in modules:
                        status= getStatus (repo['repo'], distro, release, arch, module)
                        if status.lastTried is not None:
                            # TODO: size, last amount downloaded
                            if status.lastSucceeded is not None:
                                statusFile.write ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" %
                                    (repo['repo'], distro, release, arch, module, status.lastTried.strftime ("%a %d %b, %H:%M"), status.lastSucceeded.strftime ("%a %d %b, %H:%M")))
                            else:
                                statusFile.write ("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td></td></tr>\n" %
                                    (repo['repo'], distro, release, arch, module, status.lastTried.strftime ("%a %d %b, %H:%M")))

    statusFile.write ("</table>\n")
    statusFile.close ()
