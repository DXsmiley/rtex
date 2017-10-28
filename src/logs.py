# Stuff that loggly told me to put here

import logging
import logging.handlers
import os

logger = logging.getLogger('myLogger')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('Python: { "loggerName":"%(name)s", "asciTime":"%(asctime)s", "pathName":"%(pathname)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}')


#add handler to the logger
if os.getenv('RELEASE') != None:
    handler = logging.handlers.SysLogHandler('/dev/log')
    handler.formatter = formatter
    logger.addHandler(handler)

logger.addHandler(logging.StreamHandler())

def info(text):
    logger.info(text)

def warn(text):
    logger.warning(text)

def error(text):
    logger.error(text)

def critical(text):
    logger.critical(text)