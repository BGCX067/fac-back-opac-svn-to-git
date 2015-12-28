# this contains settings used by the embedding of Helios into Horizon.

EMBEDDED_FULL_BIB_URL = "/ipac20/ipac.jsp?profile=%s&index=BIB&term=%s"

USE_HORIZON_WEB_SERVICES = 1
HORIZON_WEB_SERVICES_BASE_URL = "http://dev7:8888/webServices/ws"
AVAILABILITY_WEB_SERVICES_URL = HORIZON_WEB_SERVICES_BASE_URL + "?service=availableCopies&bib=%s&loc=%s"
REQUESTABLE_WEB_SERVICES_URL = HORIZON_WEB_SERVICES_BASE_URL + "?service=isRequestable&bib=%s"


DEFAULT_HORIZON_SEARCH_INDEX = ".GW"
HORIZON_AUTHOR_SEARCH_INDEX = ".NW"

HORIZON_SEARCH_INDEX_MAPPING = { ".GW" : "text",
                                ".EW" : "text",
                                ".SW" : "subject",
                                ".NW" : "author",
                                ".AW" : "author",
                                ".SE" : "series",
                                ".TW" : "title",
                                }
# the opposite of horizon search index mapping
HORIZON_REVERSE_SEARCH_INDEX_MAPPING = {
                                      "text" : ".GW",
                                      "subject" : ".SW",
                                      "author" : ".NW",
                                      
                                      }

HORIZON_SORT_MAPPING = { "3100049" : "pubdate desc",
                         "3100048" : "pubdate desc", # this is actually "arrival date" but that is not currently Helios indexed
                         "3100015" : "title asc",
                         "3100012" : "author asc",
                     }