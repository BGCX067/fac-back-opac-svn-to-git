from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

def item(req):
    start = time.time()
    ctx = getitemresults(req)
    
    if ctx == None:
        return HttpResponseRedirect("/catalog/")
    
    ctx['LOCAL_LOGO_LOCATION'] = LOCAL_LOGO_LOCATION
    ctx['LOCAL_INSTITUTION_NAME'] = LOCAL_INSTITUTION_NAME
    # render using appropriate format
    if ctx['format'] and ctx['format'] == "py": 
        resp = HttpResponse( pprint.pformat(ctx) )
        resp.headers['Content-Type'] = "text/plain" ; return resp
    else:
        ctx['response_time'] = "%.4f" % ( time.time() - start )
        return render_to_response("item.html", ctx )

def getitemresults(req):
    start = time.time()
    q = req.GET.get('q', None) 
    searchString = q
    limits = []
    if not q:
        return None
    index = req.GET.get('index', 'text')
    if len( index.strip() ) == 0: 
        index = 'text'
    format = req.GET.get('format', None)
    page = int( req.GET.get('page', 0) )
    startNumZeroIndex = (ITEMS_PER_PAGE * page )
    startNum = startNumZeroIndex + 1
    limit = req.GET.get('limit', None)
    if limit is not None and len(limit.strip()) > 0:
        limits = limit.split(",,")
    else:
        limits = []
    sort = req.GET.get('sort', None)        
    searchString = makeSearchString( q, index, limits, sort)
    cacheKey = "%s~%s" % (searchString, page)
    data = cache.get( cacheKey )
    if not data:
        facetURLTerm = '&facet.field='.join(facetCodes)   
        urlToGet = "http://%s/solr/select?q=%s&wt=python&facet.field=%s&facet.zeros=false&facet=true&facet.limit=%s&start=%s" % ( SOLR_SERVER, searchString, facetURLTerm, MAX_FACET_TERMS_EXPANDED, startNumZeroIndex )
        data = urllib.urlopen( urlToGet ).read()
        cache.set( cacheKey, data, SEARCH_CACHE_TIME )
    ctx = eval(data)
    ctx['format'] = format;
    numFound = ctx['response']['numFound']
    endNum = min( numFound, ITEMS_PER_PAGE * (page + 1) )
    ctx['searchString'] = searchString
    ctx['q'] = q
    if limit is not None: ctx['currentLimit'] = limit.replace('"', '%22')
    if sort is not None: ctx['currentSort'] = sort
    if index is not None: ctx['currentIndex'] = index
    # augment item results.
    count = 0
    for itemOn in ctx['response']['docs']:
        itemOn['full_bib_url'] = 'http://%s/solr/select?q=bib_num:%s&version=2.2&start=0&rows=10&indent=on' % (SOLR_SERVER, "%22" + itemOn['bib_num'] + "%22")
        itemOn['count'] = count + startNum
        count += 1
        if itemOn.has_key('isbn'):
            itemOn['isbn_numeric'] = ''.join( [ x for x in itemOn['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
        if itemOn.has_key('format'):
            formatIconURL = FORMAT_ICONS.get( itemOn['format'], None)
            if formatIconURL: itemOn['format_icon_url'] = formatIconURL
        
        #hack to put pipe delimited copy level data (location, call #, etc) into a list for each item. The list is looped through in the template
        if itemOn.has_key('copyinfo'):
            itemOn['copydetails']=[]
            for items in itemOn['copyinfo']:
                itemdetails=items.split('|')
                itemOn['copydetails'].append(itemdetails)
        
        
        #make an array out of Serials Solutions Name and URL
        if itemOn.has_key('SSdata'):
            itemOn['SSurldetails']=[]
            for items in itemOn['SSdata']:
                SSurlitemdetails=items.split('|')
                itemOn['SSurldetails'].append(SSurlitemdetails)

    return ctx

