from django.conf.urls.defaults import *
import helios.config as heliosConfig
conf = heliosConfig.__dict__    
# TODO: decide if this is a bad way of doing things and its "evilness" relative to doing 
# import * from foo, then "%(asdklfjasdf)s" % locals()


urlpatterns = patterns(     'views',
                            (r'^%(HELIOS_DEPLOY_PATH)s/$' % conf, 'index'), 
                            (r'^%(HELIOS_DEPLOY_PATH)s/about/$' % conf, 'about'),
                            (r'^%(HELIOS_DEPLOY_PATH)s/opensearchdescription.xml' % conf, 'openSearchDescription' ),
                            
                            (r'^%(HELIOS_DEPLOY_PATH)s/search/advanced/$' % conf, 'searching.advancedSearch'),
                            (r'^%(HELIOS_DEPLOY_PATH)s/search/refine/$' % conf, 'searching.refine' ),
                            (r'^%(HELIOS_DEPLOY_PATH)s/search/facet/$' % conf, 'searching.ajaxFacet'),
                            
                            
                            (r'^%(HELIOS_DEPLOY_PATH)s/search/$' % conf, 'searching.search'),
                            (r'^%(HELIOS_DEPLOY_PATH)s/embed/$' % conf, 'horizonEmbedded.hipSearch' ),
                            #(r'^catalog/js/vocab.js', 'vocab' ),
                            ('^%(HELIOS_DEPLOY_PATH)s/help/$' % conf, 'help.index' ),
                            ('^debug/(?P<cacheKey>.+)/$', 'admin.getcache' ),
                            (r'^$', 'index' ),      
                      )
