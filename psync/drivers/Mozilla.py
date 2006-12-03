###########################################################################
#    Copyright (C) 2006 by Marcos Dione                                      
#    <mdione@grulic.org.ar>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

from psync.core import Psync

class Mozilla (Psync):
    def releaseDatabases (self):
        return []

    def files (self):
        for project in self.apps:
            self.app= project[0]
            self.App= project[0].capitalize ()
            # do not use 'release'
            self.versions= project[1]
            for self.version in self.versions:
                self.template= self.archTemplates[self.archs.index (self.arch)]
                self.filename= self.template % self
                for self.lang in self.languages:
                    yield ("%(app)s/releases/%(version)s/%(arch)s/%(lang)s/%(filename)s" % self, None)
                    if self.updates:
                        self.update= "$(app)s-$(version)s.complete.mar"
                        yield ("%(app)s/releases/%(version)s/update/%(arch)s/%(lang)s/%(update)s" % self, None)

    def finalReleaseDBs (self):
        return []

# end
