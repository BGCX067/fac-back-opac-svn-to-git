# contains code for working with/processing facets.
from helios.config import *
import helios.translateFunctions as translateFunctions
import helios.logger as logger

import types

translateFunctionRefs = {}
allFacetsByCode = {}
for fOn in FACETS:
    allFacetsByCode[ fOn['code'] ] = fOn
facetCodesToNames = {}
for facetOn in FACETS:
    if facetOn.has_key("translateFunction"):
        fOn = getattr( translateFunctions, facetOn['translateFunction'] )
        if fOn is not None:
            translateFunctionRefs[ facetOn['code'] ] = fOn
    facetCodesToNames[ facetOn['code'] ] = facetOn['name']
allRefineFacets = [ f for f in FACETS if (f.has_key('refine') and f['refine'] is True) ]
allRefineFacetCodes = [ f['code'] for f in allRefineFacets ]

       
def processFacets( facetCodes, facetCounts, q, limits, doExtendedTerms = True, doColors=False ):     
    # do postprocessing on facet data --put them in a format that is easier to work
    # with in the templating language, split them up into the basic &extended
    # for toggling, and translate codes where necessary
    logger.debug( "limits is %s" % limits )   
    _facets = []
    _bestBets = []  # best bets are facet terms which contain the search term
    for facetCodeOn in facetCodes:
        facetOn = {'type' : facetCodeOn['type'], 'terms' : [], 'extended_terms' : [], 'code' : facetCodeOn['code'], 
                   'name' : facetCodeOn['name'], 'has_more' : False }
        # check to see if this facet is a cloudy one.  (This value may get set to False later on if there are not enough
        # facets.)
        if facetCodeOn['code'] in allRefineFacetCodes:
            facetOn['show_cloud_link'] = True
        else:
            facetOn['show_cloud_link'] = False
        # colors are used by the cloud view to differentiate facet types.
        if doColors:
            _color = allFacetsByCode[ facetCodeOn['code'] ].get( 'refine_color_class' , 'refine-default')
            facetOn['color'] = _color
        if facetCounts['facet_fields'].has_key( facetCodeOn['code'] ):
            facetCountList = facetCounts['facet_fields'][facetCodeOn['code'] ]    
            # this is a list of alternating facets and counts
            terms, counts = facetCountList[::2], facetCountList[1::2]
            _facetOnTerms = []
            if len(terms) < MIN_TERMS_TO_SHOW_CLOUD_LINK:
                # not enough facets to justify offering a link to the cloud.
                facetOn['show_cloud_link'] = False
            
            for i in range(len(terms)):
                # if there is a translate function associated with this facet, translate the code here.
                if translateFunctionRefs.has_key( facetCodeOn['code'] ):
                    _label = translateFunctionRefs[ facetCodeOn['code'] ]( terms[i] ).strip()
                else:
                    _label = terms[i]
                _websafeTerm = terms[i]
                #_websafeTerm = _websafeTerm.replace("'", "%27").replace("&", "%26" ).replace(" ", "_").replace('"', "%22")
                for orig,replacement in FACET_TERM_REPLACEMENTS.iteritems():
                    _websafeTerm = _websafeTerm.replace(orig,replacement)
                
                
                # TODO: see if this facet is already one of our limits; if so, remove it.
                alreadyApplied = False
                
                for limitOn in limits:
                    # using repr avoids unicode encoding errors.
                    _limitTerm = repr( u"%s:%s" % ( facetCodeOn['code'], _websafeTerm) )
                    _limitOn = repr(limitOn)    
                    if _limitTerm == _limitOn:
                        alreadyApplied = True
                if not alreadyApplied:
                    _facetOnTerms.append( dict( term=_websafeTerm, count=counts[i], label=_label) )

                # check to see if this is a "best bet"
                # nb it's not a best bet if the suggestion is already one of your limits!
                # 'in <string>' comparison requires string as left operand; can't handle Unicode
                # TODO: allow it to handle Unicode here without dying on "in"
                qTerms = [x.strip() for x in q.replace(",", " ").lower().split()]
                if (type(_label) is not types.UnicodeType):
                    numTermsMatched = 0
                    for termOn in qTerms:    
                        # split apart all words and see if each one matches (so order doesn't matter)
                        if _label.lower().find( termOn ) > -1:
                            numTermsMatched += 1
                    if numTermsMatched == len(qTerms): # all words matched 
                        isBestBet = True
                        _facetAsLimit = '%s:"%s"'  %( facetCodeOn['code'] , terms[i] )
                        for limitOn in limits:  
                        # check vs. each limit and see if they're a match -- don't want to suggest a limit already applied
                            if _facetAsLimit in limitOn:
                                isBestBet = False
                        if isBestBet:
                            _bestBets.append( dict( facetTerm=_websafeTerm, facetLabel = _label, facetIndexCode = facetCodeOn['code'], facetIndexLabel = facetCodeOn['name'] ) )           
            if doExtendedTerms and (len( _facetOnTerms ) > MAX_FACET_TERMS_BASIC):
                facetOn['has_more'] = True
                facetOn['terms'] , facetOn['extended_terms'] = _facetOnTerms[:MAX_FACET_TERMS_BASIC], _facetOnTerms[MAX_FACET_TERMS_BASIC: ]
            else:
                facetOn['terms'] = _facetOnTerms 
        
        _facets.append( facetOn )
    return _facets, _bestBets
       
        
        