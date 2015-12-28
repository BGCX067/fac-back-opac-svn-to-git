""" 
this contains standard searching views.
"""

from helios.views import *


def refine(req):
    """does a view displaying all limit/facet options as either a list or a cloud."""
    logger.debug( "refine called" )

    
    start = time.time()
    ctx = searchContext.getSearchContext(req)
    # TODO: decide if these should be object attributes instead of dict keys,
    # (whether getSearchContext should return object or dict)
    q,index,limits,handler = ctx['q'], ctx['currentIndex'], ctx['limits'], ctx['handler']
    searchString = makeSearchString( q, index, limits, handler )
    facetcloud = req.GET.get('facetcloud', '')
    
    if len( facetcloud.strip() ) == 0:
        facetcloud = None
    else:
        ctx['facetcloud'] = facetcloud
        
    # facetcloud restricts the facet cloud to just one type of facets
    # facetsToUse and facetCodesToUse here refer to which faceted fields will display in the cloud
    # allRefineFacets refers to the faceted fields which will be searched for to make the cloud
    # the search string will search on ALL facets regardless, for caching simplicity.
    if facetcloud:
        facetsToUse = [ f for f in FACETS if f['code'] == facetcloud ]
        facetCodesToUse = [ f['code'] for f in facetsToUse ]
    else:    # no facet cloud specified, will show them all
        facetCodesToUse = allRefineFacetCodes
        facetsToUse = allRefineFacets

    
    allFacetsCacheKey = "allfacets~~%s~~" % searchString
    logger.debug( "All facets cache key is %s" % allFacetsCacheKey )
    
    allFacetData = cache.get( allFacetsCacheKey )
    if not allFacetData:
        facetURLTerm = "&facet.field=".join( f['code'] for f in allRefineFacets )    # we search on all potential
        urlToGet = "http://%s/solr/select/?q=%s&wt=python&facet.field=%s&facet.zeros=false&facet=true&fl=0" % ( SOLR_SERVER, searchString, facetURLTerm, )
        logger.debug( "url to get is %s" % urlToGet )
        startFacetTime = time.time()
        allFacetData = urllib.urlopen(urlToGet).read()
        if len(allFacetData) > 0:
            cache.set( allFacetsCacheKey, allFacetData, FACET_CACHE_TIME )
        else:
            logger.error( "data length was 0 for URL \n%s\n\n" % urlToGet )
        logger.debug( "all facets cache miss took %.4f" % ( time.time() - startFacetTime ) )
    else:
        logger.debug( "all facets cache hit. %s bytes read" % len( allFacetData ) )
    
    try:
        _ctx = eval( allFacetData )
    except:
        logger.error("Unable to evaluate data: \n%s\n" % allFacetData )
        return searchError( req )
    ctx.update( _ctx )
    
    # pull facet info out of context and process it, then reinsert.
    facetCounts = ctx['facet_counts']
    del ctx['facet_counts']    
    _facets, _bestBets = facets.processFacets( facetsToUse, facetCounts, q, limits, doExtendedTerms=False, doColors=True)   
    ctx['facets']  = _facets
    if len( _bestBets ) > 0 and len( _bestBets) <= MAX_BEST_BETS:
        ctx['bestBets'] = _bestBets
    
    # assemble an object containing all facets of all types (for the "all" display)
    _allfacets = []
    for facetGroupOn in ctx['facets']:
        # TODO: only do for certain facet types specifiable in the config file?
        codeOn = facetGroupOn['code']
        colorOn = allFacetsByCode[ codeOn ].get( 'refine_color_class' , 'refine-default')
        
        labelOn = facetGroupOn['name']
        for facetOn in facetGroupOn['terms']:
            _newfacet = { 'facetGroupCode' : codeOn,
                          'facetGroupLabel' : labelOn,
                          'count' : facetOn['count'],
                          'facetLabel' : facetOn['label'],
                          'facetTerm' : facetOn['term'],
                          'color' : colorOn,
                          }
            _allfacets.append( _newfacet )
            
    # Process facets for cloud.
    # sort all facets by their count attribute
    if len( _allfacets ) <= NUM_FACET_BINS:
        # then there is *no point* in binning them -- put them all in the middle BIN and be done with it.
        for facetOn in _allfacets:
            facetOn['rank'] = ( NUM_FACET_BINS // 2 )
    else: 
        # TODO: more sophisticated ranking
        countsort = lambda x,y: cmp( x['count'], y['count'])
        _allfacets.sort( countsort )
        if ctx['rank_method'] == 'linear':
            # do rank by 'linear bin': if 100 items in sorted list, 
            # 1st 33 get "1", 2nd 33 get "2", last 34 get "3"
            # naive; looks stupid for small result sets.
            numFacets = len( _allfacets )
            binSize = numFacets // NUM_FACET_BINS
            if binSize == 0: 
                # fewer total facets than number of bins -- there is only one bin and it
                # should equal in size the number of facets total.
                binSize = numFacets
            count = 0
            binOn = 0    # 0be1
            for facetOn in _allfacets:
                if ( ( count // binSize ) > binOn ) and ( count // binSize ) < NUM_FACET_BINS :
                    # then we're on to the next bin
                    binOn +=1
                facetOn['rank'] = binOn + 1    # 0be1 
                count +=1
    # now case insensitive sort by alpha (or whatever requested) instead of count
    termsort = lambda x,y: cmp( x['facetLabel'].lower(), y['facetLabel'].lower() )
    _allfacets.sort( termsort )
    # now append sorted facets to context
    ctx['allfacets'] = _allfacets
    ctx['response_time'] = "%.4f" % ( time.time() - start )
    
    if limits:
        ctx['removeLimits'] = createRemoveLimits(limits)    
    if ctx['format'] == "py": 
        resp = HttpResponse( pprint.pformat(ctx) )
        resp.headers['Content-Type'] = "text/plain" 
        return resp  
    elif ctx['format'] == 'list':
        return render_to_response("refine-list.html", ctx)
    else:
        return render_to_response("refine.html", ctx)              

def ajaxFacet( req ):
    """does the facets for a particular field for async (ajax) loading"""
    ctx = searchContext.getSearchContext(req)
    if not ctx.has_key('facet'):
        return HttpResponse("")
    q,index,limits,handler = ctx['q'], ctx['currentIndex'], ctx['limits'], ctx['handler']
    facet = ctx['facet']
    
    searchString = makeSearchString( q, index, limits, handler )
    facetCacheKey = "ajaxfacet~~%s~~%s" % (searchString, facet)
    facetData = cache.get( facetCacheKey )
    if not facetData:
        urlToGet = "http://%s/solr/select/?q=%s&wt=python&facet.field=%s&facet.zeros=false&facet=true&facet.limit=%s&fl=score" % ( SOLR_SERVER, searchString, facet, MAX_FACET_TERMS_EXPANDED )
        startAjaxFacetTime = time.time()
        facetData = urllib.urlopen( urlToGet).read()
        cache.set( facetCacheKey, facetData, FACET_CACHE_TIME )
        logger.debug( "ajax facet took %.4f" % ( time.time() - startAjaxFacetTime ) )       
    facetCtx = eval(facetData)
    facetCounts = facetCtx['facet_counts']
    _facets, _bestBets = facets.processFacets( FACETS, facetCounts, q, limits, doExtendedTerms=True)        
    ctx['facets'] = _facets
    ctx['bestBets'] = _bestBets
    return render_to_response("ajaxFacet.html", ctx )
    
def search(req):
    start = time.time()
    ctx = searchContext.getSearchContext(req)
    # TODO: eliminate these or handle differently?
    ## TODO: resist urge to solve this problem by doing something like locals().update( ctx )
    q,index,limits,handler = ctx['q'], ctx['currentIndex'], ctx['limits'], ctx['handler']
    logger.debug( "query is %s" % q )
    sort, page = ctx['currentSort'], ctx['page']
    if not q:
        return HttpResponseRedirect("/catalog/")
    startNumZeroIndex = (ITEMS_PER_PAGE * ctx['page'] )
    startNum = startNumZeroIndex + 1
          
    searchString = makeSearchString( q, index, limits, handler)

    # 1. do search
    cacheKey = "search~~%s~~%s~~%s~~%s" % (searchString, sort, page, handler)
    data = cache.get( cacheKey )
    if not data:
        if not handler or ( handler is "standard"):
            if sort and len(sort) > 0:
                urlToGet = "http://%s/solr/select?q=%s;%s&wt=python&start=%s&fl=*,score" % ( SOLR_SERVER, searchString, sort, startNumZeroIndex)
            else:
                urlToGet = "http://%s/solr/select?q=%s&wt=python&start=%s&fl=*,score" % ( SOLR_SERVER, searchString, startNumZeroIndex)
        else:   # use non-default handler (qt parameter)
            urlToGet = "http://%s/solr/select?q=%s&qt=%s&wt=python&start=%s&sort=%s&fl=*,score" % ( SOLR_SERVER, searchString, handler, startNumZeroIndex, sort )
        searchStartTime = time.time()
        data = urllib.urlopen( urlToGet ).read()
        logger.debug( "fetched URL\n>>>>>>>>>>>>>>>>\n%s\n<<<<<<<<<<<<<<<<<<<<<<<<<<" % urlToGet )
        cache.set( cacheKey, data, SEARCH_CACHE_TIME )
        logger.debug( "search cache miss took %.4f" % ( time.time() - searchStartTime ) )      
    else: 
        logger.debug( ">>>search cache hit" )
        
    # if format is solr, at this point we short-stop the request and just return whatever the data is.
    if req.has_key("format") and req['format'] == "solr":
        resp = HttpResponse( data )
        resp.headers['Content-Type'] = "text/plain" 
        return resp
    try:
        _ctx = eval(data)
    except:
        # TODO: better error handling
        # for now just raise a 503 error and be on with it
        logger.error( "bad data for cacheKey %s" % cacheKey )
        logger.debug( "BAD DATA WAS>>>>>\n\n%s\n<<<<<<<<<\n\n" % data )
        return searchError(req)    # TODO: pass through error msg with this.
    # need to check if we got no hits
    numFound = _ctx['response']['numFound']
    if numFound is 0:
        if ctx['format'] != "rss" and ctx['format'] != "py":
            # then we are using a normal HTML view -- want no hits page for these.
            return noHits(req)   
    ctx.update( _ctx )
        
    # 2. get facet info and merge in
    facetCacheKey = "facets~~%s~~" % (searchString, )  
    facetData = cache.get( facetCacheKey )
    logger.debug( "using facetCacheKey %s" % facetCacheKey )
    if not facetData:    
        facetURLTerm = '&facet.field='.join(allFastFacetCodes)  # was all facets, now just the 'fast' ones
        urlToGet = "http://%s/solr/select/?q=%s&wt=python&facet.field=%s&facet.zeros=false&facet=true&facet.limit=%s&fl=score" % ( SOLR_SERVER, searchString, facetURLTerm, MAX_FACET_TERMS_EXPANDED )
        logger.debug( "getting facet URL>>\n\n%s\n\n" % urlToGet )
        startFacetTime = time.time()
        facetData = urllib.urlopen( urlToGet ).read()
        cache.set( facetCacheKey, facetData, FACET_CACHE_TIME )
        logger.debug( "facet cache miss took %.4f" % ( time.time() - startFacetTime ) )
        doAvail = False    # we just got the availability info, so we don't need to refresh it 
    else:   
        # we have the cached facet info, but we need to refresh the availability
        # which is cached for a much shorter time than other facets.
        availCacheKey = "availability~~%s~~" % ( searchString )
        availData = cache.get( availCacheKey )
        if not availData:
            urlToGet = "http://%s/solr/select/?q=%s&wt=python&facet.field=available&facet.zeros=false&facet=true&facet.limit=%s&fl=0" % ( SOLR_SERVER, searchString, MAX_FACET_TERMS_EXPANDED )
            availStartTime = time.time()
            availData = urllib.urlopen( urlToGet ).read()
            cache.set( availCacheKey, availData, AVAILABILITY_CACHE_TIME )
            logger.debug( "availability cache miss took %.4f" % ( time.time() - availStartTime ) )
        availCtx = eval(availData)
        doAvail = True    # to indicate that this data needs to be folded into the context later on
        
    # handle facet data
    facetCtx = eval( facetData )
    facetCounts = facetCtx['facet_counts']
    if doAvail: # then we need to inject availability info into facet data
        facetCounts['facet_fields']['available'] = availCtx['facet_counts']['facet_fields']['available']
    _facets, _bestBets = facets.processFacets( FACETS, facetCounts, q, limits)
    ctx['facets']  = _facets
    if len( _bestBets ) > 0 and len( _bestBets) <= MAX_BEST_BETS:
        ctx['bestBets'] = _bestBets    
    ctx['searchString'] = searchString    # TODO: is this necessary?
    
    profile = req.GET.get("profile", "")
    
    # augment item results.
    maxScore = ctx['response']['maxScore']
    count = 0
    for itemOn in ctx['response']['docs']:
        itemOn['full_bib_url' ] = OPAC_FULL_BIB_URL % itemOn
        if ctx['format'] == "embed":
             itemOn['full_bib_url'] += "&profile=%s" % profile
        itemOn['count'] = count + startNum
        count += 1
        if itemOn.has_key('isbn'):
            itemOn['isbn_numeric'] = ''.join( [ x for x in itemOn['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
        if itemOn.has_key('format'):
            formatIconURL = FORMAT_ICONS.get( itemOn['format'], None)
            if formatIconURL: itemOn['format_icon_url'] = formatIconURL
            if itemOn['format'] in [ "eBook", "eAudio"]:
                itemOn['is_electronic_resource'] = 1
            
            
        # create linkable versions of author names.
        _authorsOn = None
        _authorList = []
        # csd 05/30/2007: changed this to deal with duplicates in "author" Solr attribute,
        # which due to (I think) dynamic indexing bug or a Solr bug sometimes gets dupes even though the 
        # "mainauthor" and "addedauthor" attributes which comprise it do not have the dupes. 
        # ALSO, in certain cases an author can appear as both a "mainauthor" (1xx) and an "addedauthor" (7xx)
        # when the work is a translation.  Why? Ask a cataloger.
        
#===============================================================================
#        if itemOn.has_key('author'):
#            _authorsOn = itemOn['author']
#            for author in _authorsOn:
#                _authorEscaped = author.replace(" ", "_").replace("'", "%27").replace('"', '%22')
#                _authorList.append( { "author_escaped" : _authorEscaped, "author" : author } )
#            if len( _authorList ) > MAX_AUTHOR_TERMS_BASIC:
#                itemOn['author'] = _authorList[ :MAX_AUTHOR_TERMS_BASIC]
#                itemOn['more_authors'] = _authorList[ MAX_AUTHOR_TERMS_BASIC: ]
#            else:
#                itemOn['author']= _authorList
#===============================================================================
        if itemOn.has_key('mainauthor'):
            _authorsOn = itemOn['mainauthor']
            for author in _authorsOn:
                _authorEscaped = author.replace(" ", "_").replace("'", "%27").replace('"', '%22')
                _authorsAddedAlready = [ x['author_escaped'] for x in _authorList ]
                if _authorEscaped not in _authorsAddedAlready:
                    _authorRightOrder = translateFunctions.getAuthorNameRightOrder( author )                    
                    _authorList.append( { "author_escaped" : _authorEscaped, "author" : _authorRightOrder } )
        if itemOn.has_key('addedauthor'):
            _authorsOn = itemOn['addedauthor']
            for author in _authorsOn:
                _authorEscaped = author.replace(" ", "_").replace("'", "%27").replace('"', '%22')
                _authorsAddedAlready = [ x['author_escaped'] for x in _authorList ]
                if _authorEscaped not in _authorsAddedAlready:
                    _authorRightOrder = translateFunctions.getAuthorNameRightOrder( author )               
                    _authorList.append( { "author_escaped" : _authorEscaped, "author" : _authorRightOrder } )            
        if len( _authorList ) > MAX_AUTHOR_TERMS_BASIC:
            itemOn['author']= _authorList[ :MAX_AUTHOR_TERMS_BASIC]
            itemOn['more_authors'] = _authorList[ MAX_AUTHOR_TERMS_BASIC: ]
        else:
            itemOn['author']= _authorList
            
        # create normalized score field
        _score =  itemOn['score']
        del itemOn['score']
        itemOn['score'] =  "%.3f" % round(  (( _score + 0.0) / maxScore), 3 )
    ctx['startNum'] = startNum
    ctx['endNum'] = min( numFound, ITEMS_PER_PAGE * (page + 1) )

    if ctx['format'] == "embed":
        ctx['pagination'] = doPagination( page, numFound, ITEMS_PER_PAGE, isZeroIndexed=False)
    else:
        ctx['pagination'] = doPagination( page, numFound, ITEMS_PER_PAGE)
    # put together "remove your limit" options
    if limits:
        if ctx.has_key('format') and ctx['format'] == "embed":
            
            ctx['removeLimits'] = createRemoveLimits(limits, embedded=True)
        else:
            ctx['removeLimits'] = createRemoveLimits(limits)
    ctx['response_time'] = "%.4f" % ( time.time() - start )
    
    # render using appropriate format
    if not ctx.has_key("format"):
        # if no format specified, use standard search format
        return render_to_response("search.html", ctx )  
    if ctx['format'] == "py": 
        # we will go through the ctx and "unflatten" the marc record so it will pretty print
        for docOn in ctx['response']['docs']:
            marcRecordOn = docOn['marc_record']
            docOn['marc_record'] = eval( marcRecordOn )    
        resp = HttpResponse( pprint.pformat(ctx) )
        resp.headers['Content-Type'] = "text/plain" 
        return resp
    elif ctx['format'] == "rss":
        resp = render_to_response("search-rss.html", ctx)
        resp.headers['Content-Type'] = "text/xml; charset=UTF-8"
        return resp
    elif ctx['format'] == "grid":
        # do post-processing on the results to split up into rows for the grid view
        # (this is nigh-well impossible to do in templating language...)
        _docs = ctx['response']['docs']
        _rows = []
        _rowOn = []
        _counter = 0
        for docOn in _docs:
            if len(_rowOn )>= ITEMS_PER_ROW_GRID_VIEW:
                _rows.append( _rowOn )
                _rowOn = []
            _rowOn.append( docOn )
        if len( _rowOn ) > 0:
            # append partial last row if it exists
            _rows.append( _rowOn )
        ctx['response']['rows'] = _rows
        return render_to_response("search-grid.html", ctx)
    elif ctx['format'] == "embed":
        # stick in special stuff for embedded search not used by others
        import horizonEmbeddedConfig
        import horizonEmbeddedUtils
        ctx['profile'] = profile
        ctx['hipindex'] = req.GET.get('hipindex', "")
        ctx['currentLimit'] = ctx['currentLimit'].replace(":", "--")    # TODO: deal with this ugly hack
        ctx['embeddedConfig'] = horizonEmbeddedConfig
        ctx = horizonEmbeddedUtils.addHorizonWebServicesInfo( ctx )
        ctx['response_time'] = "%.4f" % ( time.time() - start )    
        return render_to_response("search-embed.html", ctx)
    else:
        return render_to_response("search.html", ctx )

