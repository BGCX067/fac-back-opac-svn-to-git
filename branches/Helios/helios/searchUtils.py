# utilities used in the searching process.
import urllib
import helios.logger as logger
import translateFunctions
from helios.config import *

allFacetCodes = [ f['code'] for f in FACETS ]
facetCodesToNames = {}
translateFunctionRefs = {}
# this collects references to all of the translation functions used by particular facets for easy
# usage later on.  
for facetOn in FACETS:
    if facetOn.has_key("translateFunction"):
        fOn = getattr( translateFunctions, facetOn['translateFunction'] )
        if fOn is not None:
            translateFunctionRefs[ facetOn['code'] ] = fOn
    facetCodesToNames[ facetOn['code'] ] = facetOn['name']
    
def makeSearchString(q, index, limits, handler=None):   # sort, 
    """translates search parameters into Solr query syntax."""
    q = q.replace("_", " ")
    
    # strip out stopwords here... this is necessary due to some 
    # unexpected side-effects of the general keyword search
    # TODO: do NOT strip stopwords if a quoted search, eg. "the the" or "to be or not to be"
    qWords = q.split(" ")
    nonStopWords = []
    for wordOn in qWords:
        if wordOn not in STOPWORDS:    
            nonStopWords.append( wordOn )
    q = " ".join(nonStopWords)
    
    for orig,replacement in SEARCH_CHARACTER_REPLACEMENTS.iteritems():
        q = q.replace(orig,replacement)
    q = urllib.quote( q ).strip()
     
    if not handler or (handler is "standard"):
        if index in allFacetCodes:    
            # then treat as an exact match search; it is a facet, not free text entered by user
            ret = '%s:"%s"' % (index, q)
        else:    
            # then it is a search index, not a facet -- NOT exact match
            ret = '%s:%s' % (index, q)
    else:   
        # if you specify a handler you can't also specify an index...
        ret = '%s' % q
    for limitOn in limits:
        # csdebug: how are these forbidden characters making it this far?
        _limOn = urllib.unquote( limitOn )
        
        
        limitSplit = _limOn.split(":")
        logger.error("limitSplit is %s\n\n\n\n" % limitSplit) # csdebug
        index = limitSplit[0]    # todo error handling
        term = ":".join( limitSplit[1:] )
        for orig,replacement in SEARCH_CHARACTER_REPLACEMENTS.iteritems():
            term = term.replace(orig,replacement)
            logger.error("\n\nterm is now %s\n\n" % term)
        logger.error("\n\nxxterm is now %s\n\n" % term)
        term = term.replace("_", " ")
        #.replace('"', "") 
        term = term.strip()
        logger.error("\n\nyyterm is now %s\n\n" % term)
        # we are going to put exact quotes around the whole thing, so we don't want to double-quote
        term = urllib.quote(term)
        logger.error("\n\n!!!term is now %s\n\n" % term)
        ret = """%s AND %s:"%s\"""" % ( ret, index, term)
    # get rid of any double spaces.
    ret = ret.replace("  ", " ")
    ret = ret.replace(" ", "%20")
    logger.debug( "search string is %s" % ret )  
    return ret.strip()

def createRemoveLimits( limits, embedded=False ):
    removeOptions = []    
    for limitOn in limits:
        allOtherLimits = ",,".join( [x for x in limits if x != limitOn] )
        # TODO: deal with possibilty of : appearing in one of the faceted terms
        
        chunks = limitOn.split(":")
        if len(chunks) == 2:
            index,term = chunks
        elif len(chunks) > 2:
            index = chunks[0]
            term = ":".join( chunks[1:] )
        else:
            logger.info("Bad limit term -- no colon found in %s" % limitOn )
            continue
        rawterm = term
        indexTranslated = facetCodesToNames[ index ]
        term = term.replace('"', '').replace("_", " ").replace("'", "")
        if translateFunctionRefs.has_key( index ):    # then we need to translate codes
            termTranslated = translateFunctionRefs[ index ]( term )
        else:
            termTranslated = term
        label = "%s: %s" % ( indexTranslated, termTranslated )
        #_searchThisTerm = "%s:%s" % (_index, _term)
        if embedded:
            allOtherLimits = allOtherLimits.replace(":", "--")    # in the embedded view cannot use colons!
        removeOptions.append( { 'label' : label, 'index' : index, 'term' : rawterm,  'new_limit' : allOtherLimits} )
    return removeOptions

