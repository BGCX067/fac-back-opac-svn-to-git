"""
This contains views used for administrative/diagnostic purposes.

"""

from savitr.views import *

def getcache( req, cacheKey ):
    """this view allows you to retrieve the raw data from the cache for debugging purposes"""
    resp= cache.get( cacheKey, None)
    if resp == None: resp = ""
    print "resp length is %s" % len(resp)
    try:
        resp = eval(resp) # transforming to object will allow pformat to pretty print it.
    except:
        pass
    httr =  HttpResponse( pprint.pformat( resp ) )
    httr.headers['Content-Type'] = "text/plain"
    return httr
