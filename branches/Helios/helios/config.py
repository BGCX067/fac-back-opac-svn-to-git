#-------------------------------------------------------------------------------
# Begin stuff you will need to configure
#-------------------------------------------------------------------------------

SOLR_SERVER = "dev7:8888" 
HELIOS_BASE_URL = "http://catalog.spl.org"    # used by OpenSearch.  External base URL of Helios server.
HELIOS_DEPLOY_PATH = "catalog"    
# the application path of Helios.  {{HELIOS_BASE_URL}}/{{HELIOS_DEPLOY_PATH}}/ should take you to the front screen of Helios

OPAC_FULL_BIB_URL = "http://catalog.spl.org/ipac20/ipac.jsp?index=BIB&term=%(bib_num)s"

LIBRARY_NAME = "The Seattle Public Library"
LIBRARY_LOGO_URL = "http://catalog.spl.org/hipres/logos/SPL_horiz_sm_color4.gif"
LIBRARY_LOGO_URL_LARGE = "http://www.spl.org/images/g_spl_logo.gif"
LIBRARY_BASE_URL = "http://catalog.spl.org/"    # used in RSS feeds.
LIBRARY_SHORT_NAME = "SPL" # can be the same as LIBRARY_NAME.  Used by OpenSearch
LIBRARY_CONTACT = "someone@example.com" # email address of contact person.  Used by OpenSearch.
USE_SYNDETICS = True
LIBRARY_SYNDETICS_ID = "Syndetics_ID_Here" 

# this is the icon that displays when no cover jacket exists for a particular book.  NOte that it is JUST the URL,
# not the HTML like in the FORMAT_ICONS dict.  It has to be that way for the javascript that uses it.
NO_HITS_ICON = "http://catalog.spl.org/hipres/images/formaticons/ipac-icon-book.gif"

FORMAT_ICONS = {    'eAudio' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-eaudio.gif" alt="eAudio" />',
                    'eBook' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-ebook.gif" alt="eBook" />',
                    'CD-ROM' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-cdrom.gif" alt="cd rom" />',
                    'Book On Cassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-bt.gif" alt="book on cassette" />',
                    'Book On CD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-bkcd.gif" alt="book on CD" />',
                    'Cassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-audio.gif" alt="cassette" />',
                    'Music CD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-cd.gif" alt="music cd" />',
                    'Phono Record' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-record.gif" alt="phono record" />',
                    'DVD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-dvd.gif" alt="dvd" />',
                    'Videocassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-video.gif" alt="videocassette" />',
                    'Large Print Book' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-largeprint.gif" alt="large print book" />',
                    'Book' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-book.gif" alt="book" />',
                    'Magazine' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-magazine.gif" alt="magazine" />',
                    'Map' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-map.gif" alt="map" />',
                    'Musical Score' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-score.gif" alt="musical score" />',
                    'Digital Music' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-digimusic.gif" alt="digital music" />',
}
                    
LOCATION_NAMES = { 'bal': 'Ballard Branch', 'bea': 'Beacon Hill Branch', 'bro': 'Broadview Branch',
                 'cap' : 'Capitol Hill Branch', 'cen' : 'Central Library', 'col': 'Columbia Branch',
                 'dlr' : 'Delridge Branch', 'dth' : 'Douglass-Truth Branch', 'glk': 'Greenlake Branch',
                 'hip' : 'Highpoint Branch', 'mag' : 'Magnolia Branch', 'mgm' : 'Madrona Branch',
                 'mon' : 'Montlake Branch', 'net' : 'Northeast Branch', 'nhy' : 'New Holly Branch',
                 'qna' : 'Queen Anne Branch' , 'rbe' : 'Rainier Beach Branch', 'swt' : 'Southwest Branch',
                 'uni' : 'University Branch', 'wal' : 'Wallingford Branch', 'wlb' : 'Washington Talking Book & Braille Library',
                 'wts' : 'West Seattle Branch', 'fre' : 'Fremont Branch', 'gwd' : 'Greenwood Branch',
                 'idc' : 'International District/Chinatown Branch', 'lcy' : 'Lake City Branch', 'nga' : 'Northgate Branch',
                 'tcs' : 'Technical and Collections Services', 'mob' : 'Mobile Services', 'spa' : 'South Park Branch',
                 'qas' : 'Queen Anne Storage', 'ill' : 'Interlibrary Loan',
                }

#------------------------------------------------------------------------------------------------------------
# End of stuff you need to configure.


LOG_LEVEL = "debug"    # possible values are critical, error, warning, info and debug.

# NB currently setting this to true will write ALL log messages to stdout, not just ones 
# above the current log level.  That is because you should NOT be using this feature unless
# you're debugging (it slows things down, may make mod_python blow up, etc.)
LOG_TO_STDOUT = True


DEFAULT_SEARCH_HANDLER = "casey2-b"  # this is the search handler used for relevancy & General KW.  it needs to match
                                    # up to a valid requestHandler in solrconfig.xml.  needs to be "standard"
                                    # to use the non-DisMax handler.  
SEARCH_CACHE_TIME = 1200    # 20 minutes in seconds    (search results)
FACET_CACHE_TIME = 43200    # 12 hours in seconds    (facet counts)
AVAILABILITY_CACHE_TIME = 60   # 1 minute in seconds (item availaibility)

# how many items display in the standard list view.
ITEMS_PER_PAGE = 10
# how many items display on each row of the grid view.
ITEMS_PER_ROW_GRID_VIEW = 4
# how many items display on each page of the grid view (NOT YET IMPLEMENTED)
ITEMS_PER_PAGE_GRID_VIEW = 20
MAX_FACET_TERMS_BASIC = 4    # how many facet terms display by default
MAX_FACET_TERMS_EXPANDED = 25 # how many facet terms display when you hit "show more"
MAX_AUTHOR_TERMS_BASIC = 3   # if more than this many authors, additional ones are hidden by expander
MAX_BEST_BETS = 5   # if more than this many 'best bets', the bets aren't very good; don't show any of them.
MIN_TERMS_TO_SHOW_CLOUD_LINK = 10 # if a facet has less than this number of terms, the "Cloud" link isn't offered.

   
USE_YAHOO_SPELLING_WEB_SERVICE = True
# please get your own one of these if you're going to be doing anything too insane with Helios.
YAHOO_APPID = "9.E82EjV34HyJQRpm_BmwnFkokrif4gs4ddQA5_swvHEa8Ch0ylWSsxdfOXWcme1AD75lIq6"
YAHOO_WEB_SERVICE_URL = "http://search.yahooapis.com/WebSearchService/V1/spellingSuggestion?appid=%(YAHOO_APPID)s&output=json&query=%(query)s"
YAHOO_SPELLCHECK_CACHE_TIME = 86400 # == 24 hours in seconds


FACETS = [   
          # all facets here must be a defined facet in your solr records.   The name is what you want it
          # called in labels.  the code is what will be used in URL syntax.  The type can be either fast
          # or slow.  Fast facets areloaded the first time through; slow facets are loaded with AJAX after
          # the rest of the page.  if refine is True, it is presented as one of the options on cloud.
          # refine_color_class is the CSS class used in the cloud
          
           # available at is still EXPERIMENTAL 
            #  { 'name' : 'Checked In At', 'code' : 'available', 'type' : 'fast', 
            #   'translateFunction' : 'getLocationName' , 'refine' : False  },
              { 'name' : 'Topic', 'code' : 'topic', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-royalblue'},  
              
               { 'name' : 'Format', 'code' : 'format', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-green' },

             # you may want to change this to "fast" if you don't mind Helios taking a bit longer to load
              { 'name' : 'Author/Performer', 'code' : 'author_exact', 'type' : 'slow', 'refine' : True, 'refine_color_class' : 'refine-red', 
               'translateFunction' : 'getAuthorNameRightOrder'},
              
                            
               { 'name' : 'Language', 'code' : 'language', 'type' : 'fast', 'refine' : True },   
              { 'name' : 'Audience', 'code' : 'audience', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-darkyellow' },   
              { 'name' : 'Person', 'code' : 'subjectname' , 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-blue'},                   
              { 'name' : 'Region', 'code' : 'place', 'type' : 'fast', 'refine' : True,'refine_color_class' : 'refine-darkred' },    
              { 'name' : 'Era', 'code' : 'era', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-brown' },
              { 'name' : 'Genre', 'code' : 'genre', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-purple' },
          # classification is not in general all that useful, it turns out.
           #   { 'name' : 'Classification', 'code' : 'deweyclass', 'type' : 'fast', 
           #    'translateFunction' : 'getDeweyClassName', 'refine' : True, 'refine_color_class' : 'refine-dodgerblue' },
              { 'name' : 'Owned By' , 'code' : 'location', 'type' : 'fast', 'maxItems' : 0 , 
               'translateFunction' : 'getLocationName', 'refine' : False }, 
               { 'name' : 'Series', 'code' : 'series', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-darkgreen'},
               
              { 'name' : 'Publisher' , 'code' : 'publisher', 'type' : 'fast', 'refine' : True, 'refine_color_class' : 'refine-orange' },
              
              ]
# the number of bins used in the "refine" display
NUM_FACET_BINS = 10



SEARCH_INDEXES = [ {'name' : 'Anywhere', 'index': 'text'},
                  {'name' : 'Author', 'index': 'author'} , { 'name' : 'Title', 'index' : 'title' },
                   {'name' : 'Subject', 'index': 'subject'}, { 'name' : 'ISBN', 'index' : 'isbn' },
                   {'name' : 'Accession' , 'index' : 'bib_num' }, ]
SORTS = [{ 'name' : 'Publication Date (newest first)', 'direction' : 'desc', 'field' : 'pubdate' },
         { 'name' : 'Publication Date (oldest first)', 'direction' : 'asc', 'field' : 'pubdate' },
         { 'name' : 'Author A-Z', 'direction' : 'asc', 'field' : 'author_exact' },
         #{ 'name' : 'Title A-Z', 'direction' : 'asc', 'field' : 'title' },
         # TODO: make title sort work.
         # For this to work, need to have exact match title field (title_exact)
         
         #{ 'name' : 'Purchase Date (newest first)', 'direction' : 'desc', 'field' : 'bib_num' },
         # TODO: make this work.
         # For accession # (purchase date) to work as a sort must be copied to a non-string field in Solr config.
         ]

# ADVANCED_SEARCH_OPTIONS contains the controlled vocabulary terms on the advanced search screen
# it should contain a dict of dicts mapping from type of controlled vocabulary to a dict consisting
# of code -> label mappings
# this is also used by the advanced search view directly 
# TODO: finish this.
ADVANCED_SEARCH_OPTIONS = {
                       'Format' : {
                            'eAudio' : 'Downloadable Audio',
                            'eBook' :  'Downloadable Book',
                            'CD-ROM' : 'CD-ROM',
                            'Book on Cassette' : 'Book on Cassette',       
                       },
                       'Language' :{
                             'eng' : 'English',
                                     
                       },  
                       'Checked In At' : LOCATION_NAMES,
}

# These are for a "limit to your current location" for OPACs at a particular location (NOT YET IMPLEMENTED)
# key = location code, value = list of individual IP addressses ( strings )  or ranges ( tuples of two strings )      
# you should ONLY specify small ranges here.  it does not compute these efficiently (stores a key/value pair for
# every IP address within the range), so if you put in something like 
# ( '10.0.0.1', '11.0.0.1') you WILL crash your computer.
# you can specify   
DO_LOCATION_IP_ADDRESS_RANGES = False
            
LOCATION_IP_ADDRESS_RANGES = {
    'bal' : [   ( '66.212.67.145', '66.212.67.159'),
                ( '66.212.73.65', '66.212.73.127'),
            ],
    'bea' : [   ( '66.212.66.145', '66.212.66.159'),
                ( '66.212.73.129', '66.212.73.190'),
            ],
    'bro' : [   ( '66.212.72.65', '66.212.72.127'),
                ( '66.212.67.81', '66.212.67.95' ),
            ],
    'cap' : [   ( '66.212.66.193', '66.212.66.206' ),
                ( '66.212.70.193', '66.212.70.254' ),
            ],
    'col' : [   ( '66.212.67.97' , '66.212.67.111' ),
                ( '66.212.72.129', '66.212.72.191' ),
            ],
    'dlr' : [   ( '66.212.68.225', '66.212.68.254' ),
                ( '66.212.66.33' , '66.212.66.47' ),
            ],
    'dth' : [   ( '66.212.66.161', '66.212.66.174' ),
                ( '66.212.70.65', '66.212.70.127' ),
            ],
    'cen' : [   ( '66.212.76.1' , '66.212.77.254' ),
                ( '66.212.78.1' , '66.212.79.254' ),
                ( '66.212.67.192', '66.212.67.254' ),
            ],
    'fre' : [   ( '66.212.66.1', '66.212.66.15' ),
                ( '66.212.68.161' , '66.212.68.191' ),
            ],
    'glk' : [   ( '66.212.67.129', '66.212.67.173' ),
                ( '66.212.73.1', '66.212.73.63' ),
            ],
    'gwd' : [   ( '66.212.67.65' , '66.212.67.79' ),
                ( '66.212.72.1', '66.212.72.63' ),
            ],
    'hip' : [   ( '66.212.66.113' , '66.212.66.127'),
                ( '66.212.68.33', '66.212.68.63' ),
            ],
    'idc' : [   ( '66.212.67.1', '66.212.67.15' ),
                ( '66.212.69.97' , '66.212.69.127' ),
            ],
    'lcy' : [   ( '66.212.67.33' , '66.212.67.45' ),
                ( '66.212.71.129', '66.212.71.191' ),
            ],
    'mag' : [   ( '66.212.66.17' , '66.212.66.31' ),
                ( '66.212.68.193' , '66.212.68.223' ),
            ],
    'mgm' : [   ( '66.212.69.1', '66.212.69.31' ),
                ( '66.212.66.49' , '66.212.66.63' ),
            ],
    'mon' : [   ( '66.212.71.1', '66.212.71.63' ),
                ( '66.212.66.81' , '66.212.66.95' ),
            ],
    'net' : [   ( '66.212.67.113', '66.212.67.127' ),
                ( '66.212.72.193' , '66.212.72.254' ),
            ],
    'nga' : [   ( '66.212.67.17', '66.212.67.31' ),
                ( '66.212.71.65', '66.212.71.127' ),
            ],
    'nhy' : [   ( '66.212.66.129', '66.212.66.143' ),
                ( '66.212.68.65' , '66.212.68.95' ),
            ],
    'qna' : [   ( '66.212.66.97', '66.212.66.111' ),
                ( '66.212.68.1', '66.212.68.31' ),
            ],
    'rbe' : [   ( '66.212.67.177', '66.212.67.191' ),
                ( '66.212.74.1', '66.212.74.63' ),
            ],
    'spa' : [   ( '66.212.66.209', '66.212.66.223' ),
                ( '66.212.68.129' , '66.212.68.159' ),
            ],
    'swt' : [   ( '66.212.73.193', '66.212.73.254' ),
                ( '66.212.67.161', '66.212.67.175' ),
            ],
    'uni' : [   ( '66.212.67.49', '66.212.67.73' ),
                ( '66.212.71.193', '66.212.71.254' ),
            ],
    'wts' : [   ( '66.212.66.177', '66.212.66.191' ),
                ( '66.212.70.129', '66.212.70.191' ),
            ],
    'wlb' : [   ( '66.212.66.65', '66.212.66.79' ),
                ( '66.212.69.33', '66.212.69.63' ),
            ],
}

# following are used to strip out stopwords from searches (because the relevancy-ranking
# search handler in Solr gets confused by stopwords)
# this default list taken from Solr's stopwords.txt
STOPWORDS = [ "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it",
"no", "not", "of", "on", "or", "s", "such", "t", "that", "the", "their", "then", "there", "these", "they", "this",
"to", "was", "will", "with" ]

# this is a mapping of special characters to what they should be replaced with when they
# are in a search term.
SEARCH_CHARACTER_REPLACEMENTS = {
                                 #';' : ' ', 
                                 # must strip semicolons and colons not to mess up lucene syntax
                                 #':' : ' ',
                                 #'!' : ' ',
                                 # we must escape all punctuation that might break lucene here. 
                           #      "'" : "%27",
                           #"&" : "%26",
                           #" " : "_",
                           #'"' : "%22",
                           #":" : "%3A",
                           #";" : "%3B",
}
    
SORT_CHARACTER_REPLACEMENTS = {
                               " " : "%20",
                               "_" : "%20",
                               }
# used to create the wikipedia-style slug terms for facets' you've applied to your search
FACET_TERM_REPLACEMENTS = {
                           "'" : "%27",
                           "&" : "%26",
                           " " : "_",
                           '"' : "%22",
                           ":" : "%3A",
                           ";" : "%3B",
}

#
HELIOS_VERSION = "1.06 Beta 1"