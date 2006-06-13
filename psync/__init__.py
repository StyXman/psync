# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>

import logging
import sys

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s",
                              '%H:%M:%S')
# formatter = logging.Formatter(
#     "%(asctime)s %(levelname)-8s %(filename)8s:%(lineno)-3s %(message)s",
#     '%H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger('psync')
logger.addHandler(handler)

logLevel= logging.INFO
