
from config import *
from utils import *
import time
addressLocationMap = parseLocationIPAddressRanges( LOCATION_IP_ADDRESS_RANGES )

allFacetsByCode = {}
for fOn in FACETS:
    allFacetsByCode[ fOn['code'] ] = fOn

def doPresentation():
    ret = dict( NO_HITS_ICON = NO_HITS_ICON, 
                HELIOS_VERSION = HELIOS_VERSION,
                LIBRARY_BASE_URL =LIBRARY_BASE_URL, 
                LIBRARY_CONTACT = LIBRARY_CONTACT,
                LIBRARY_NAME = LIBRARY_NAME, 
                LIBRARY_SHORT_NAME = LIBRARY_SHORT_NAME,
                LIBRARY_LOGO_URL_LARGE = LIBRARY_LOGO_URL_LARGE, 
                LIBRARY_LOGO_URL = LIBRARY_LOGO_URL,
                HELIOS_DEPLOY_PATH = HELIOS_DEPLOY_PATH,
                HELIOS_BASE_URL = HELIOS_BASE_URL,
                )
    if USE_SYNDETICS:
        ret['LIBRARY_SYNDETICS_ID'] = LIBRARY_SYNDETICS_ID
    return ret

def getSearchContext( req ):
    """returns a dictionary with standard data used by all search views."""
    # TODO: rearrange this code so it is easier to follow.
    
    #logger.debug( "type of req is %s" % type(req) )
    
    ret = {}
    userAgent = req.META['HTTP_USER_AGENT']
    ret['userAgent'] = userAgent
    ret['isIE'] = (userAgent.find("MSIE") > -1)
    
    format = req.GET.get('format', 'normal')
    ret['format'] = format
    q = qDisplay = req.GET.get( 'q', None )
    if q is not None:
        qDisplay = qDisplay.replace("_" , " ")
    ret['q'] = q
    ret['qDisplay'] = qDisplay
    index = req.GET.get( 'index', 'text' )
    if (index is None) or len( index.strip() ) == 0:
        index='text'
    ret['currentIndex'] = index 
    limits = []
    limit = req.GET.get('limit', None )
    if limit is not None and len( limit.strip() ) > 0:
        limits = limit.split(",,")
    if (len(limits) > 0) or (index != "text"):
        handler = "standard"
    else:
        handler = req.GET.get( 'handler', DEFAULT_SEARCH_HANDLER)
    ret['handler'] = handler
    ret['limits'] = limits
    sort = req.GET.get( 'sort', '')
    # TODO: abstract these replace() elements out 
    if limit is not None:
        ret['currentLimit'] = limit
    if sort is not None:
        # currentSortEscaped is only used by embedded view at this point.
        # TODO: figure out if still necessary or if fixed on java/xsl side
        ret['currentSortEscaped'] = sort.replace( "%20", "_" ).replace(" ", "_")
        
        for orig,replacement in SORT_CHARACTER_REPLACEMENTS.iteritems():
            sort = sort.replace( orig, replacement )
            
        ret['currentSort']  = sort.strip()
    if DO_LOCATION_IP_ADDRESS_RANGES:
        loc = req.GET.get( 'location' , None )
        if loc and len(loc) == 0:
            loc = None
        # 2. if not in URL, check by IP address.
        if not loc:
            logger.debug( "remote addr is %s" % req.META['REMOTE_ADDR'] )
            asInt = IPAddressToInt( req.META['REMOTE_ADDR'] )
            loc = addressLocationMap.get( asInt, None )
        # if loc is still None at this point, we will not offer the 'this location' option
        if loc is not None:
            ret['loc'] = loc
    rank = req.GET.get( 'rank', 'linear')
    ret['rank_method'] = rank
    _sorts = SORTS
    for sortOn in _sorts:
        _sortOnCoded = "%s%%20%s" % ( sortOn['field'], sortOn['direction'])
        sortOn['selected'] = ( ret['currentSort'] == _sortOnCoded ) 
    ret['sorts'] = _sorts    
    ret['PRESENTATION'] = doPresentation()
    page = int( req.GET.get('page', 0) )
    ret['page'] = page
    # TODO: num per page here
    
    # TODO: we need to make sure that the SEARCH_INDEXES includes the current index
    # if not, stick it in (so the search you just did is always a searching option)
    #ret['indexes'] = SEARCH_INDEXES
    _searchIndexes = SEARCH_INDEXES

    ret['indexes'] = _searchIndexes 
    
    _facet = req.GET.get( 'facet', None)
    if _facet is not None:
        ret['facet'] = _facet
    
    ret['lastBuildDate'] = time.strftime( "%a, %d %b %Y %H:%M:%S %Z")
    # TODO: is this right syntax for RSS?

    return ret
    