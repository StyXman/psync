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

        for self.lang in self.languages:
            subLangs= self.subLanguages[self.languages.index (self.lang)]
            for self.subLang in subLangs:
                logger.debug (self.__dict__)
                yield (self.filenameTemplate % self, None)
                # if self.withJRE:
                #     yield ("stable/%(release)s/OOo_%(release)s_%(arch)s_install_wJRE.%(ext)s" % self, None)

                yield ("contrib/dictionaries/Math_%(lang)s_%(subLang)s.zip" % self, None)
                yield ("contrib/dictionaries/README_Math_%(lang)s_%(subLang)s.txt" % self, None)
                yield ("contrib/dictionaries/README_%(lang)s_%(subLang)s-rh.txt" % self, None)
                yield ("contrib/dictionaries/README_%(lang)s_%(subLang)s.txt" % self, None)
                yield ("contrib/dictionaries/README_hyph_%(lang)s_%(subLang)s.txt" % self, None)
                yield ("contrib/dictionaries/README_th_%(lang)s_%(subLang)s.txt" % self, None)
                yield ("contrib/dictionaries/%(lang)s_%(subLang)s-pack.zip" % self, None)
                yield ("contrib/dictionaries/%(lang)s_%(subLang)s.zip" % self, None)
                yield ("contrib/dictionaries/hyph_%(lang)s_%(subLang)s.zip" % self, None)
                yield ("contrib/dictionaries/thes_%(lang)s_%(subLang)s.zip" % self, None)
                yield ("contrib/dictionaries/thes_%(lang)s_%(subLang)s_v2.zip" % self, None)

    def finalReleaseDBs (self, old=False):
        return []

# end
