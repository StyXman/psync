# (c) 2006
# Marcos Dione <mdione@grulic.org.ar>

from psync.core import Psync

from psync import logLevel
import logging
logger = logging.getLogger('psync.drivers.OpenOfficeOrg')
logger.setLevel(logLevel)

class OpenOfficeOrg (Psync):
    # TODO: download indexes and get stat from them
    # no localized support... yet?
    def releaseDatabases (self):
        return []

    def files (self):
        self.ext= self.exts[self.archs.index (self.arch)]

        yield ("stable/%(release)s/OOo_%(release)s_%(arch)s_install.%(ext)s" % self, None)
        if self.withJRE:
            yield ("stable/%(release)s/OOo_%(release)s_%(arch)s_install_wJRE.%(ext)s" % self, None)

        for self.lang in self.languages:
            subLangs= self.subLanguages[self.languages.index (self.lang)]
            for self.subLang in subLangs:
                yield ("contrib/dictionaries/%(lang)s_%(subLang)s.zip" % self, None)
                if False:
                    yield ("contrib/dictionaries/%(lang)s_%(subLang)s-pack.zip" % self, None)

    def finalReleaseDBs (self):
        return []

# end
