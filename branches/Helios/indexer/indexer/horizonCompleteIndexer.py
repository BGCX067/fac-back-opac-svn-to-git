
# Casey Durfee 4.9.2007 <casey.durfee@spl.org>
# this file handles all necessary indexing for Horizon.
# it checks every n minutes (configured in config.solr) for PMS/MARC files in the index-queue directory
# and handles them. It also checks/updates item statuses.  
# Other scripts handle actually getting the PMS files into that directory and 
# doing the mass reindex (so it does not have to run on your day end machine).

from java.lang import *
from java.util import *
from org.marc4j import *
from org.marc4j.converter.impl import *
from config.solr import * 
import time
import horizonItemStatus
import horizonIncrementalIndexer
import facetWarmer
import solrConnection

        
    
if __name__ == '__main__':
    print "[%s] Horizon complete indexer starting" % time.ctime()
    converter = AnselToUnicode()
    checkInterval = long(INCREMENTAL_INDEXER_SLEEP_INTERVAL) # in seconds
    optimizeInterval = long(INCREMENTAL_INDEXER_OPTIMIZE_INTERVAL)
    optimizeCountInterval = long( INCREMENTAL_INDEXER_OPTIMIZE_COUNT)
    facetWarmInterval = long( INCREMENTAL_INDEXER_FACET_WARM_INTERVAL )
    doItemStatusIndexing = int( DO_ITEM_STATUS_INDEXING )
    doItemStatusYesterdayRefresh = int( DO_ITEM_STATUS_YESTERDAY_REFRESH)
    numThreads = int( INCREMENTAL_INDEXER_MAX_THREADS )
    doInitialWarming = int( INCREMENTAL_INDEXER_INITIAL_WARMING)
    deleteAfterIndexing = int( DELETE_MARC_RECORDS_FROM_INDEX_QUEUE )
    
    # NOTE: we *cannot* use a job scheduler like Quartz here because we don't want overlapping jobs or jobs building up.
    lastRunTime = lastOptimizeTime = lastFacetWarmTime = time.time()
    firstTime = 1
    keepgoing = 1
    count = 0
    startDate = int( time.strftime("%d") )
    while keepgoing:
        now = time.time()
        ## 1st do incremental indexing if nec.
        if firstTime or ( (now - lastRunTime) >= checkInterval ):
            if firstTime and doInitialWarming:
                #a. warm facets if the very first time it has run
                facetWarmer.warmFacets()
                lastFacetWarmTime = time.time()
            # b. check for PMS/MARC files in indexer-queue directory and handle if necessary.
            # NOTE: it only does this check the first time through, so setting deleteAfterIndexing to false
            # will not cause the same files to keep getting reindexed.
            count += horizonIncrementalIndexer.processFilesInDirectory("./indexer-queue", anselUnicodeConverter = converter, numThreads=numThreads, deleteAfterIndexing=deleteAfterIndexing)
            print "[%s] done processing indexer-queue contents" % time.ctime()
            
            # c. do status changes.
            if doItemStatusIndexing:
                count += horizonIncrementalIndexer.incrementalIndexingJob(commitNonblocking=1)    
            lastRunTime = time.time()
            firstTime = 0
        else:
            print "not time to run yet, last ran %.4f ago" % (now-lastRunTime)
        ## 2nd do optimize if nec.
        now = time.time()
        justOptimized =0
        if optimizeInterval:
            if( (now - lastOptimizeTime) >= optimizeInterval ):
                print "[%s] optimizing" % time.ctime()
                solrConnection.optimize()
                lastOptimizeTime = time.time()
                justOptimized = 1
        if count > optimizeCountInterval and (not justOptimized):
            print "count is %s, forcing OPTIMIZE" % count
            solrConnection.optimize()
            count = 0
        ## 3rd do facet warm if necessary.
        now = time.time()
        if facetWarmInterval:
            if( (now - lastFacetWarmTime) >= facetWarmInterval ):
                print "[%s] facets haven't been warmed in %.4f; warming them" % (time.ctime(), ( now-lastFacetWarmTime) )
                facetWarmer.warmFacets()
                lastFacetWarmTime = time.time()
        ## 4th do complete refresh of yesterday's modified records, if necessary.
        if doItemStatusYesterdayRefresh:
            currentDate = int( time.strftime("%d") )
            if currentDate != startDate:
                print "adding all records modified yesterday to the queue."
                horizonItemStatus.reindexRecordsModifiedYesterday()
                print "done retrospective reindexing"
                startDate = currentDate
        nextRunTime = lastRunTime + checkInterval
        diff = nextRunTime - time.time()
        if diff > 0:
            print "sleeping for %.4f" % diff
            time.sleep(diff)
        