import logging
import asyncio


logging.basicConfig(level=logging.INFO)
indi_logger = logging.getLogger('IndiClient')

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('./indi_error.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
indi_logger.addHandler(c_handler)
indi_logger.addHandler(f_handler)


INDI_DEBUG = True
INDI_LOG_DATA = False


# asyncio events

blob_event1 = asyncio.Event()
blob_event2 = asyncio.Event()