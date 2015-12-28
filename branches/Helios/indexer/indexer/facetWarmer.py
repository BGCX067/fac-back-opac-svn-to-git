"""
Warms up faceted searching by doing large searches over all faceted fields 

"""
import urllib, time, sys

from config.solr import *


WARMUP_QUERY = "q=text:[a%20TO%20z]"    # this should theoretically load all records in DB

# TODO: pull FACETS_TO_DO from config.solr
FACETS_TO_DO = [ 'author_exact', 'publisher', 'pubdate', 'audience', 'language', 'genre', 'place',
                'topic', 'subjectname', 'subjectentity', 'title', 'format']

FACET_LIMIT = 10

def warmFacets( server=SOLR_SERVER, warmupQuery=WARMUP_QUERY, facets =FACETS_TO_DO, facetLimit = FACET_LIMIT ):
    # 1. first we try and hit all records in the DB
    query = "http://%s/solr/select/?%s&fl=*&wt=python" % (server, warmupQuery )
    print "query is %s" % query
    u= urllib.urlopen( query )
    data = u.read()
    resp = None
    try:
        resp = eval(data)
        print "%s records indexed" % ( resp['response']['numFound'] )
    except:
        print "problem eval()ing data"
        
    u.close()
    # 2. now do a query on each facet parameter
    for facetOn in facets:
        query = "http://%s/solr/select/?%s&wt=python&facet=true&facet.field=%s&facet.zeros=true&rows=0&facet.limit=%d" % (server, warmupQuery, facetOn, FACET_LIMIT)
        start = time.time()
        u = urllib.urlopen( query )
        data = u.read()
        u.close()
        print "query on facet %s took %.4f" % (facetOn, time.time() - start)
        #print "\n%s\n" % query

if __name__ == '__main__':
    if len(sys.argv) > 1:
        server = sys.argv[1]
    else:
        server = SOLR_SERVER
    warmFacets( server, WARMUP_QUERY, FACETS_TO_DO )
    print "done!"
    