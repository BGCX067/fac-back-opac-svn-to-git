# all the settings in this file are considered GLOBAL and not tied to a particular namespace.

SOLR_SERVER = "dev5:8080" 


INCREMENTAL_INDEXER_SLEEP_INTERVAL = 15            # in seconds

# set these to 0 to have the index not perform these steps
INCREMENTAL_INDEXER_OPTIMIZE_INTERVAL = 6000       # in seconds
INCREMENTAL_INDEXER_FACET_WARM_INTERVAL = 3000     # in seconds
INCREMENTAL_INDEXER_OPTIMIZE_COUNT = 10000        # in records (force optimize after this many records created/updated/deleted)
INCREMENTAL_INDEXER_INITIAL_WARMING = 0

# maximum number of parallel workers you want running.  If = 10 will process 10 files from the indexer-queue
# simultaneously.
INCREMENTAL_INDEXER_MAX_THREADS = 100

# whether indexed MARC files should be deleted from indexing queue after done processing 
# (set to 1 unless debugging)
DELETE_MARC_RECORDS_FROM_INDEX_QUEUE = 0

DO_ITEM_STATUS_INDEXING =0
DO_ITEM_STATUS_YESTERDAY_REFRESH = 0    
# whether the indexer should, just after midnight, refresh all records with item statuses modified the day before.
# this prevents accumulation of errors in the index.


SOLR_INDEX_BATCH_SIZE = 10
SOLR_COMMIT_BATCH_SIZE = 2000
SOLR_OPTIMIZE_BATCH_SIZE = 500000    # how often to run an <optimize /> command while indexing files.
PRINT_SOLR_POST_DATA = 0    #

# you should not need to change any of the following.
SOLR_BASE_URL = "http://%s/solr" % SOLR_SERVER
SOLR_UPDATE_URL = "%s/update/" % SOLR_BASE_URL
SOLR_QUERY_URL = "%s/select/" % SOLR_BASE_URL
SOLR_COMMIT_MESSAGE = "<commit/>"
SOLR_COMMIT_NONBLOCKING_MESSAGE = """<commit waitFlush="false" waitSearcher="false" />"""
SOLR_OPTIMIZE_MESSAGE = "<optimize/>"
SOLR_DELETE_ID_MESSAGE = "<delete><id>%(recordID)s</id></delete>"
SOLR_DELETE_ALL_MESSAGE = "<delete><id>*:*</id></delete>"
NUM_RECORDS_TO_ADD = 10000000

