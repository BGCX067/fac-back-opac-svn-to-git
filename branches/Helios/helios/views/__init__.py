# generic, non-searching views, and utilities/constants/imports used by all views.

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.cache import cache
from helios.config import *
import helios.logger as logger
from utils import *
from searchUtils import *
import facets
import translateFunctions
import searchContext

import urllib, pprint, time, types

## TODO: figure out how much of this stuff is still needed after refactor
allFacetCodes = [ f['code'] for f in FACETS ]
allFacets = FACETS
allFacetsByCode = {}
for fOn in FACETS:
    allFacetsByCode[ fOn['code'] ] = fOn
allFastFacets = [ f for f in FACETS if f['type'] == 'fast' ]
allFastFacetCodes = [ f['code'] for f in allFastFacets ]
allRefineFacets = [ f for f in FACETS if (f.has_key('refine') and f['refine'] is True) ]
allRefineFacetCodes = [ f['code'] for f in allRefineFacets ]


# TODO: decide if there's a better place to put this.
addressLocationMap = parseLocationIPAddressRanges( LOCATION_IP_ADDRESS_RANGES )

def openSearchDescription(req):
    ctx = searchContext.getSearchContext(req)
    resp = render_to_response("openSearchDescription.html", ctx)
    resp.headers['Content-Type'] = "application/opensearchdescription+xml"
    return resp
    

def about(req):
    ctx = searchContext.getSearchContext(req)
    # we do not want the search box on the "about" screen to contain anything.
    # TODO: fix this hack by making getSearchContext return appropriate thing based on view
    del ctx['q']
    del ctx['qDisplay']    
    #ctx['PRESENTATION'] = searchContext.doPresentation()
    return render_to_response("about.html", ctx)

def advancedSearch(req):
    """this supplies the advanced search interface"""
    ctx = searchContext.getSearchContext(req)
    return render_to_response( "search-advanced.html", ctx)

def index(req):
    ctx = {}
    ctx['PRESENTATION'] = searchContext.doPresentation()
    return render_to_response("index.html", ctx )

# TODO: cache decorator
def vocab(req):
    """this returns a javascript object with the controlled vocabularies used by the advanced
    search interface"""
    foo = { 'pants' : 'meat', 'original' : ['nope',] }
    from django.utils import simplejson
    vocabTerms = {}
    # Controlled vocabulary contains:
    # locations
    # formats
    # languages
    # audience
    
    resp = HttpResponse( simplejson.dumps( ADVANCED_SEARCH_OPTIONS ) )
    resp.headers['Content-Type'] = "application/x-javascript" # TODO: is this right content type???
    return resp
    



def searchError( req ):
    #return HttpResponse("there was an error with your search. The problem has been logged.")
    ctx = searchContext.getSearchContext( req )
    return render_to_response( "error.html", ctx )

def noHits(req):
    #return HttpResponse("no hits found!")
    import spelling
    ctx = searchContext.getSearchContext( req )
    # TODO: try the cache for suggestions first
    # TODO: keep some kind of counter on Yahoo web service use so we don't break the internet
    fromSpellcheck = req.GET.get('spellcheck', None)
    if fromSpellcheck is not None:
        ctx['spellcheck_failed'] = 1
    else:
        suggestions = spelling.spellCheck( ctx['qDisplay'] )
        if len(suggestions) > 0:
            ctx['spelling_suggestions' ] = suggestions
        
    # TODO: check against spellchecker here
    return render_to_response( "noHits.html", ctx)


