# (c) 2005
# Marcos Dione <mdione@grulic.org.ar>

import logging

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s",
                                '%H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger('psync')
logger.addHandler(handler)

logLevel= logging.INFO
