"""
Indexes records from Solr.
"""
from java.lang import *
from java.io import *
from java.net import *
from org.marc4j import *
from org.marc4j.converter.impl import *
import time, sys, urllib

import horizonItemStatus
import facetWarmer
import solrConnection
import solrIndexingUtils
from config.solr import *

PROFILE = 1 # if true, provides advanced performance profiling.

DO_ACCESSION = 0 # if false, MUST be an accession number in 999$a

DEFAULT_INDEXING_PROPERTIES_FILE = "config/indexer.properties"

class processFileJob( Runnable ):
    def __init__(self, filename, anselUnicodeConverter = None, nonblocking = 0, pid = 0):
        self.filename = filename
        self.anselUnicodeConverter = anselUnicodeConverter
        self.nonblocking = nonblocking
        self.pid = pid
    def run(self):
        print "processFileJob %s starting" % self.pid
        processFile( self.filename, anselUnicodeConverter=self.anselUnicodeConverter, nonblocking=self.nonblocking, pid=self.pid)
        print "processFileJob %s done processing" % self.pid

def processFile( filename, anselUnicodeConverter = None, nonblocking = 0, pid=-1 ):
    # if nonblocking == 0 then all commits are blocking; if 1 then they are nonblocking.
    inStream = FileInputStream(filename)
    print "processFile>> %s" % filename
    marcReader = MarcStreamReader( inStream )
    data = ""
    count = 0
    lastCommitTime = None
    import time
    startTime = time.time()
    lastRecord = None
    lastBibNum = None
    m4j = None
    marcReaderTime = 0
    marcRecordToDictTime = 0
    extractorCreateTime = 0
    extractionTime = 0
    extractMethodTime = 0
    marcRecordForSolrTime = 0
    commitTime = 0
    updateTime = 0
    marcSerializeTime = 0
    accession = 0   # TODO: try and load serialized accession # from somewhere
    serializedRecord = None
    recordBatch = []
    # get default properties file
    from loadPropsFile import *
    props = loadPropsFile( DEFAULT_INDEXING_PROPERTIES_FILE )
    
    while marcReader.hasNext() and count < NUM_RECORDS_TO_ADD:
        #if pid > -1:
        #    print (".%d" % pid),
        #else:
        #    print ".",
        # CSDEBUG    
        accession += 1  
        count += 1
        # TODO: improve error handling here (main problem is that Marc4J will fall over
        # at the sight of a bad record and there's no way to get it to just skip over
        # a bad record -- so there is little we can do, except better error messages!
        try:
            mrTimeStart = time.time()                
            marc4jRecord = marcReader.next()
            marcReaderTime += ( time.time() - mrTimeStart )                
        except:
            print "last record indexed was bib# %s " % lastBibNum
            import sys
            print "sys.exc_info is %s" % str(sys.exc_info())
            sys.exit(1)
                

        mrsTime = time.time()
        #try:
        rec = solrIndexingUtils.recordForSolr( marc4jRecord, anselUnicodeConverter, propsObject = props)
        #except:
        #    print "exception processing record, skipping"    # TODO: error handling
        #    continue
        marcRecordForSolrTime += ( time.time() - mrsTime )
        extractionTime += rec._extractionTime
        extractorCreateTime += rec._extractorCreateTime
        marcRecordToDictTime += rec._marcRecordToDictTime
        extractMethodTime += rec._extractMethodTime  
        
        if hasattr( rec, "bib_num"):
            recordBatch.append( rec )
            lastBibNum = rec.bib_num
        else:
            print "not adding record %s; no bib_num present!" % rec
            
        if( (count % SOLR_INDEX_BATCH_SIZE ) == 0):
           # nb. neither apache commons nor python urllib works right here!  Unicode gets mangled.  
           #Must use postURL
           
           # fetch the item status info if required.
            if DO_ITEM_STATUS_INDEXING:
                bibs = [x.bib_num for x in recordBatch]
                avail = horizonItemStatus.availableAt( bibs )
                for x in recordBatch:
                    x.available = avail[ x.bib_num ]
            
            mrserTime = time.time()  
            data = u''.join( [ x.serialize() for x in recordBatch] )
            recordBatch = []
            marcSerializeTime += ( time.time() - mrserTime )
            
           
            startUpdateTime = time.time()
            try:
                resp = solrConnection.postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data)

            except IOError:
                print "Connection reset when talking to Solr, skipping this commit and sleeping 10 sec."
                time.sleep(10)
                resp = solrConnection.postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data)
                # if it fails again here, we want to just bomb out.
            if resp.find( '<result status="1"') > -1:
                print "\nError POSTing documents!  Response from Solr was\n\n%s\n" % resp   
            # TODO: put in retry/continue code here for failed updates/slowdowns on Solr
            # TODO: parse result status and do something if there is an error (like print stacktrace)
            updateTime += ( time.time() - startUpdateTime )
            if pid > -1:
                print ("*%d" % pid),
            else:
                print "*",
            if PRINT_SOLR_POST_DATA:
                print "\n\n<add>%s</add>\n\n" % data
            data = ""
        if( ( count % SOLR_COMMIT_BATCH_SIZE) == 0):
            try:
                print "committing..."
                beginCommitTime = time.time()
                if nonblocking:
                    print "doing nonblocking commit"
                    solrConnection.commitNonblocking()
                else:
                    solrConnection.commit()
                commitTime += ( time.time() - beginCommitTime )
            except IOError:
                import time
                print "Connection reset when talking to Solr, skipping this commit and sleeping 10 sec."
                time.sleep(10)
            if lastCommitTime:
                thisBatchRate = ( ( 0.0 + SOLR_COMMIT_BATCH_SIZE) / (time.time() - lastCommitTime) )
                overallRate = ( ( 0.0 + count ) / ( time.time() - startTime) )
                if pid > -1:
                    print "\n>>>>>>>>>>>>COMMIT for PID %s<<<<<<<<<<<<<<<\n" % pid # csdebug
                print "[%s] %s records indexed\t| This Batch: %.4f records/sec|\tOverall: %.4f records/sec" % (time.ctime(), count, thisBatchRate, overallRate)
                if PROFILE:
                    print """\nfile->MARC: %.4f\nMARC->py: %.4f\npy->XML: %.4f\n""" % ( marcReaderTime, marcRecordForSolrTime, marcSerializeTime )
                    print """MARC to dict: %.4f\ncreate extractor: %.4f\nextraction: %.4f\n\textract method: %.4f""" % ( marcRecordToDictTime, extractorCreateTime, extractionTime, extractMethodTime )
                    print """Solr Update: %.4f\nSolr Commit: %.4f\n""" % ( updateTime, commitTime )                          
            lastCommitTime = time.time()
        if( (count % SOLR_OPTIMIZE_BATCH_SIZE) == 0):
            print "[%s] FORCING OPTIMIZE..." % time.ctime()
            solrConnection.optimize()
            print "[%s] OPTIMIZE done" % time.ctime()
            System.gc()
    # do last batch here
    if len(recordBatch) > 0:
        print "doing final POST"
        mrserTime = time.time()
        data = ''.join( [ x.serialize() for x in recordBatch] )
        recordBatch = []
        
        resp = solrConnection.postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data)
        if resp.find( '<result status="1"') > -1:
            print "\nError POSTing documents!  Response from Solr was\n\n%s\n\n" % resp        
    print "committing..."
    if nonblocking:
        solrConnection.commitNonblocking()
    else:
        solrConnection.commit()         
    inStream.close()
    return count
            
            
if __name__ == '__main__':
    anselUnicodeConverter = AnselToUnicode()
    # 2 arguments to command line are used to do a ran
    if len(sys.argv) == 2:
        processFile( sys.argv[1], anselUnicodeConverter )
    else:
        print "incorrect usage -- specify file to be processed."
        sys.exit(1)
    print "done indexing, now optimizing"
    optimize()
    print "done optimizing, now warming facets"
    from facetWarmer import *
    for i in range(3):
        # running warmFacets more than once appears to improve performance.
        facetWarmer.warmFacets( server=SOLR_QUERY_URL )
    
    print "all done!"
                
    
        
        
