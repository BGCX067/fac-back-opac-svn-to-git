from helios.views import *    # this makes all the crud loaded/imported in __init__ accessible in here
import helios.views.searching as normalSearching
from horizonEmbeddedConfig import *
    
def hipSearch(req):
    """Provides embedded search capability from within HIP.  This method just transforms
    the HIP search parameters to Helios-ese and then dishes it off to the standard
    searching.search method to handle."""
    format = "helios" 
    filter = req.GET.get('filter' )
    pg = req.GET.get( 'page', '0' )
    page = int( pg )
    if page > 0:
        page = page -1    # 0be1 -> because Horizon is 1 indexed and helios is 0 indexed.
    try:
        index,sort,limit,source = filter.split("~~")
    except:
        return HttpResponse("invalid filter argument")
    if source != "helios":    # all arguments are horizon-style; need to translate parameters before dishing off
        if len(index.strip() ) == 0:
            index = DEFAULT_HORIZON_SEARCH_INDEX
        indexTranslated = translateIndex(index)
        hipindex = index
        sortTranslated = translateEmbeddedSort( sort )
    else:    # this is mostly helios-style; just need to unpack the "filter" string
        limit = limit.replace("--", ":")
        indexTranslated = index
        hipindex = untranslateIndex( index )
        sortTranslated = sort
    getCopy = req.GET.copy()
    getCopy['index'] = indexTranslated
    getCopy['hipindex'] = hipindex
    getCopy['sort'] = sortTranslated
    getCopy['limit'] = limit
    getCopy['source'] = source
    getCopy['format'] = "embed"
    getCopy['page'] = page
    
    req.GET = getCopy
    return normalSearching.search( req )

def translateEmbeddedSort( sort ):
    if len(sort) > 0:
        sortTranslated = HORIZON_SORT_MAPPING.get( sort, None)
        if sortTranslated is not None:
            return sortTranslated.replace(" ", "%20")
    # default case: return None
    return None
def translateIndex( index ):
    return HORIZON_SEARCH_INDEX_MAPPING.get(index, None)

def untranslateIndex(index):
    return HORIZON_REVERSE_SEARCH_INDEX_MAPPING.get(index, DEFAULT_HORIZON_SEARCH_INDEX )

def makeEmbeddedSearchString( term, index, limit, handler=None):
    """creates a search string from URL passed from Horizon, using the settings in 
    horizonEmbeddedConfig.py to map between the two systems.""" 
    ret = ""
    if len(index) == 0:
        index = DEFAULT_HORIZON_SEARCH_INDEX
    indexTranslated = HORIZON_SEARCH_INDEX_MAPPING.get( index, DEFAULT_HORIZON_SEARCH_INDEX)
    if not handler or (handler is "standard"):
        if indexTranslated in allFacetCodes:
            ret = '%s:"%s"' % (index, term)
        else:    # then it is a search index, not a facet -- NOT exact match
            ret = '%s:%s' % (index, term)
    else:   # you can't have an index with a non-default term
        ret = "%s" % term

    # TODO: limits!
    return urllib.quote(ret).strip()