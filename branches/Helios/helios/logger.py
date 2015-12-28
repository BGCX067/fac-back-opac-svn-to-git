# the python built-in logging module is overengineered and confusing (and requires you to 
# initialize a different logger for each app.)  this is a slight improvement.  it allows you
# to have a central logging facility for all apps, and it tells you exactly what
# line of what file is doing the logging.

import logging, logging.handlers, inspect, sys
from helios.config import *

# these are coming from helios config
logFileName = locals().get('LOG_FILE', "helios.log")
logLevel = locals().get('LOG_LEVEL', 'info')
logToStdOut = locals().get('LOG_TO_STDOUT', True)

handler = logging.handlers.TimedRotatingFileHandler( logFileName, when="midnight", backupCount=10 )

formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter( formatter )
loggers = {}

defaultLogger = logging.getLogger('default')
defaultLogger.addHandler( handler )

if logLevel == "critical":
    defaultLogger.setLevel( logging.CRITICAL)
elif logLevel == "error":
    defaultLogger.setLevel( logging.ERROR)
elif logLevel == "warning":
    defaultLogger.setLevel( logging.CRITICAL)
elif logLevel == "info":
    defaultLogger.setLevel( logging.INFO )
else:
    defaultLogger.setLevel( logging.DEBUG )

defaultLogger.info( 'logging initialized at level %s.  All messages at a lower level will be ignored.' % logLevel )

def _doLog(message, level):
    """note that _doLog should not ever be called directly because it uses sys._getframe(2)"""
    prevframe = sys._getframe(2)
    callingPackageName = prevframe.f_globals['__name__']
    callingFunctionName = prevframe.f_code.co_name
    callingLineNumber = prevframe.f_lineno
    calledBy = "%s.%s" % ( callingPackageName, callingFunctionName )
    loggerOn = loggers.get( calledBy, None)
    if not loggerOn: 
        loggerOn = logging.getLogger( calledBy )
        loggerOn.addHandler( handler )
        if logLevel == "critical":
            loggerOn.setLevel( logging.CRITICAL )
        elif logLevel == "error":
            loggerOn.setLevel( logging.ERROR )
        elif logLevel == "warning":
            loggerOn.setLevel( logging.INFO )            
        elif logLevel == "info":
            loggerOn.setLevel( logging.INFO )
        else: 
            loggerOn.setLevel( logging.DEBUG )
        loggers[calledBy] = loggerOn
    messageToPrint = "[%s:%s] %s" % (calledBy, callingLineNumber, message)        
    if level == "critical":
        loggerOn.critical( messageToPrint )
    elif level == "error":
        loggerOn.error( messageToPrint )
    elif level == "warning":
        loggerOn.warning( messageToPrint )
    elif level == "info":
        loggerOn.info( messageToPrint )
    elif level == "debug":
        loggerOn.debug(messageToPrint )
    if logToStdOut:
        print messageToPrint
        
def critical(message):
    _doLog(message, "critical")
def error( message ):
    _doLog( message, "error")
def warning( message ):
    _doLog( message, "warning")
def info( message ):
    _doLog( message, "info" )
def debug( message ):
    _doLog( message, "debug" )
                