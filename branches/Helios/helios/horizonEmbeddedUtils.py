"""
This module provides various utilities which are used by the horizon embedded version of 
Helios.  These mostly interface with Horizon Web Services, which is a completely separate product.
"""

from horizonEmbeddedConfig import *
import urllib, time

def addHorizonWebServicesInfo( ctx ):
    """this takes in the context object and injects in info from horizon web services"""
    bibs = []
    start = time.time()
    for docOn in ctx['response']['docs']:
        bibs.append( docOn['bib_num'] )
    loc = ctx['profile']
    sBibs = ",".join( [str(x) for x in bibs] )
    urlToUse = HORIZON_WEB_SERVICES_BASE_URL + "?services=availableCopies,isRequestable&bib=%s&loc=%s"  % (sBibs, loc)
    print "requesting URL %s" % urlToUse #csdebug
    data = urllib.urlopen( urlToUse ).read()
    allAvailables,allRequestables = data.split("~~")
    availables = allAvailables.split("!!")
    requestables = allRequestables.split("!!")
    if len(availables) == len(requestables) and len(availables) == len(bibs):
        counter = 0
        for docOn in ctx['response']['docs']:
            docOn['holdsInfoHTML'] = availables[counter]
            docOn['is_requestable'] = int(requestables[counter])
            counter +=1
    else:
        print "got wrong number of responses when doing addHorizonWebServicesInfo"
    print "took %.5f to add horizon web services info" % ( time.time() - start )
    return ctx

def getHoldsInfoHTML( bib, loc ):
    """returns HTML for the item availability display."""
    start = time.time()
    data = urllib.urlopen( AVAILABILITY_WEB_SERVICES_URL % ( bib, loc) ).read()
    print "Availability>> took %.5f secs for %s" % (time.time() - start, bib )   # csdebug
    return data

def getIsRequestable( bib ):
    """returns whether or not a certain bib# should present the option of requesting"""
    start = time.time()
    data = urllib.urlopen( REQUESTABLE_WEB_SERVICES_URL % bib ).read()
    ret = 0
    try:
        ret = int(data)
    except:
        pass
    print "IsRequestable>> took %.5f secs for %s" % (time.time() - start, bib )
    return ret