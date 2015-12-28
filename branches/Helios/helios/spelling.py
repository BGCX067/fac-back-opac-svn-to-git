# controls the spellchecking feature of Helios
# currently uses Yahoo! Web service api to do this.

import config
import django.utils.simplejson as simplejson
import urllib
import types
from django.core.cache import cache
import helios.logger as logger

def spellCheck( phraseToCheck ):
    """takes the phrase to check and returns a list of potential suggestions."""
    ret = []
    if not config.USE_YAHOO_SPELLING_WEB_SERVICE:
        pass
    else:        
        # TODO: will it handle utf8?
        
        # check cache first.
        cacheKey = "spellcheck~~%s~~" % phraseToCheck
        
        suggestionsFromCache = cache.get( cacheKey )
        if not suggestionsFromCache:
            query = urllib.quote( phraseToCheck )
            
            urlToGet = config.YAHOO_WEB_SERVICE_URL % dict( YAHOO_APPID = config.YAHOO_APPID, query = query )
            logger.debug("fetching URL %s" % urlToGet )
            data = urllib.urlopen( urlToGet ).read()
            try:
                respObject = simplejson.loads( data )
                # note we do this to prevent caching bad data
                cache.set( cacheKey, data, config.YAHOO_SPELLCHECK_CACHE_TIME)
                # TODO: figure out if it will *ever* return multiple suggestions...
            except:
                logger.error( "exception doing spellCheck service" )
        else:
            logger.debug( "got spelling suggestion from cache") 
            respObject = simplejson.loads( suggestionsFromCache )
        #print "respObject is %s, type is %s" % (respObject, type(respObject) )    # csdebug
        if respObject.has_key("ResultSet") and type(respObject['ResultSet']) == types.DictType and respObject['ResultSet'].has_key("Result"):
            ret.append( respObject['ResultSet']['Result'] )
    logger.debug("returning %s" % ret)
    return ret

                
    #return ['pants', 'pantaloons']    # csdebug
    