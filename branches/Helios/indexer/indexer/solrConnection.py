"""
methods for connecting to Solr
"""

from java.io import *
from java.net import *
from config.solr import *


def postURL( url, data, contentType="""text/xml; charset="utf-8" """ ):
    """POSTs data to URL using utf-8"""
    u = URL( url )
    hu = u.openConnection()
    hu.setFollowRedirects(1)
    hu.setDoOutput(1)
    hu.setRequestMethod("POST")
    hu.setRequestProperty("Content-Type", contentType )
    osw = OutputStreamWriter( hu.getOutputStream(), "UTF8")
    osw.write( data )
    osw.flush()
    osw.close()
    inStream = hu.getInputStream()
    br = BufferedReader( InputStreamReader( inStream ) )
    lineOn = ""
    ret = ""
    while lineOn is not None:
        ret += lineOn
        lineOn = br.readLine()
    inStream.close()    # csdebug -- not closing stream causing too many open files?
    return ret

def optimize(url =SOLR_UPDATE_URL):
    postURL( url, SOLR_OPTIMIZE_MESSAGE )

def commit( url = SOLR_UPDATE_URL ):
    postURL( url, SOLR_COMMIT_MESSAGE )

def commitNonblocking( url = SOLR_UPDATE_URL):
    postURL( url, SOLR_COMMIT_NONBLOCKING_MESSAGE )

def deleteRecord( recordID, url = SOLR_UPDATE_URL):
    postURL( url, SOLR_DELETE_ID_MESSAGE % locals() )
