"""
Utilities for handling record updates from Horizon.  Horizon allows the ability to output
a file nightly of changed MARC records, called a PMS (Pending MARC Send) file.
"""
HORIZON_BASE_DIR = "c:/Horizon73"
BETWEEN_RECORD_DELIMITER = "\x1E\x1D"
DO_OPTIMIZE = 1    # optimize

from java.lang import *
from org.marc4j.converter.impl import *
import glob, os, time
import indexerDriver
import solrConnection
import facetWarmer

def processPMSFile( fInName ):
    """takes the name of a PMS file, extracts just the MARC data from it, writes it to a file,
    and returns the name of the file just created and a list of bibs that should be deleted."""
    fOutName = "%s.MARC" % fInName
    fIn = open( fInName )
    marcRecords = []    # this is the best way to avoid a lot of string concatenation.
    deletedBibs = []
    lines = fIn.readlines()    # must do this because jython, not pure python so can't do for line in file:
    fIn.close()
    for lineOn in lines:
        if not lineOn.startswith("B"):
            pass
        # find start of MARC record (after 3rd comma in string )
        else:
            commaAt = 0
            for i in range(3):
                commaAt = lineOn.find(",", commaAt+1)
            assert commaAt != 0, "problem parsing line!!!"
            dataOn = lineOn[ commaAt+1: ].strip()
            # if this is not a delete command, add it to the data
            if dataOn[5] == 'd':    # indicates this is a deleted record
                bib = lineOn.split(",")[0][1:]  # b123345,asdf,... -> 123345
                print "adding delete command for %s" % bib
                deletedBibs.append( bib )
            else:
                marcRecords.append( dataOn )
    if len(marcRecords) >0 :
        data = BETWEEN_RECORD_DELIMITER.join( marcRecords )
        data += BETWEEN_RECORD_DELIMITER    # need this after last one...
        fOut = open( fOutName, "w" )
        fOut.write( data )
        fOut.flush()
        fOut.close()
    else:
        fOutName = None
    return fOutName, deletedBibs


def processFilesInDirectory(dirName, anselUnicodeConverter = None, commitNonblocking =0, numThreads = 1, deleteAfterIndexing = 1):
    """processes MARC and PMS files in the indexer-queue directory.  If numThreads > 1
    it will try to parallelize the MARC record processing (but not PMS indexing -- no reason for that)     
    """
    pmsFiles = glob.glob( "%s/PMS*.DAT" % dirName )
    updatedAnyRecords = 0
    count= 0
    for fileOn in pmsFiles:
        print "processing PMS file %s" % fileOn
        processedFilenameOn, deletedBibsOn = processPMSFile(fileOn)
        if processedFilenameOn:
            print "processing MARC file %s" % processedFilenameOn
            indexerDriver.processFile( processedFilenameOn, anselUnicodeConverter )
            
            # now that we are done processing the file, we delete it.
            print "deleting MARC file %s " % processedFilenameOn
            os.remove( processedFilenameOn )
            print "deleting PMS file %s" % fileOn
            os.remove( fileOn )
            
            if deletedBibsOn:
                print "processing deleted bibs from MARC file %s" % processedFilenameOn
                for bibOn in deletedBibsOn:
                    print "deleting bib %s" % bibOn
                    indexerDriver.deleteRecord( bibOn )
            updatedAnyRecords = 1
        else:
            print "no records to index"
            os.remove( fileOn )

    print "[%s] now checking for MARC files" % time.ctime()
    _marcFiles = glob.glob( "%s/*.MARC" % dirName)
    _marcFiles += glob.glob ("%s/*.marc" % dirName )
    _marcFiles += glob.glob ("%s/*.dat" % dirName )
    _marcFiles += glob.glob ("%s/*.DAT" % dirName )
    _marcFiles += glob.glob( "%s/*scriblio*" % dirName )
    # dedupe _marcFiles here incase a file matches more than one glob
    # using a dictionary is the fastest way to dedupe a list with Jython
    marcFileDict = {}
    for fileOn in _marcFiles:
        marcFileDict[fileOn] = None
    marcFiles = marcFileDict.keys()
    marcFiles.sort()
    
    numMarcFiles = len(marcFiles)
    print "[%s] found %d files to process." % (time.ctime(), numMarcFiles )
    if numThreads == 1:
        for fileOn in marcFiles:
            print "processing MARC file %s" % fileOn
            count = indexerDriver.processFile( fileOn, anselUnicodeConverter, nonblocking=1 ) # csdebug: added nonblocking here
            updatedAnyRecords = 1
            if deleteAfterIndexing:
                os.remove( fileOn )
    elif numThreads >= numMarcFiles:
        # spin off a thread for each one
        # was getting weird problems with multithreading (AttributeErrors when trying to iterate
        # over all controlFields in MARC record -- trying separate anselUnicodeConverters to see if that's the issue.
        threads = []
        threadrefs = []
        i = 0
        for fileOn in marcFiles:
            convOn = AnselToUnicode()
            jobOn = indexerDriver.processFileJob( fileOn, convOn, nonblocking = 1, pid = i)# csdebug: handle nonblocking option
            _threadOn = Thread( jobOn, "process file job %s" %i )
            threads.append( _threadOn )
            threadrefs.append( jobOn )
            print "starting thread %s processing file %s" % (i, fileOn)
            _threadOn.start() 
            i += 1
            updatedAnyRecords = 1
        print "joining threads"
        for i in range( len(threads) ):
            threads[i].join()
            # TODO: make sure the thread was successful before nuking.
            if deleteAfterIndexing:
                print "deleting %s" % threadrefs[i].filename
                os.remove( threadrefs[i].filename )
            
    else:
        # do work queue here.
        print "not yet implemented"
    # finally, do a commit here.
    if updatedAnyRecords:
        print "[%s] starting final commit" % time.ctime()
        if commitNonblocking:
            solrConnection.commitNonblocking()
        else:
            solrConnection.commit()
        print "[%s] done committing" % time.ctime()
    return count



def incrementalIndexingJob(commitNonblocking=0):
    """the incremental indexing job scans for changed bibliographic records from Horizon and updates
    them accordingly in Solr."""
    bibsToUpdate = horizonItemStatus.getChangedBibs(doDelete=0) 
    print "\n[%s] updating %s bibs" % ( time.ctime(), len(bibsToUpdate) )
    bibCount = 0
    recordBatch = []
    for bibOn in bibsToUpdate:
        bibCount +=1
        availAt = horizonItemStatus.availableAt( bibOn )
        newRecordOn = horizonItemStatus.updateSolrRecordAvailability( bibOn, availAt, doPost = 0)
        recordBatch.append( newRecordOn )
        # now delete item from queue
        horizonItemStatus.deleteFromIndexQueue( bibOn )
        print "-",
        if ( (bibCount % SOLR_INDEX_BATCH_SIZE) == 0):
            data = u''.join( recordBatch )
            print "*",
            resp = solrConnection.postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data )
            recordBatch = []
        print ("+%s+" % bibOn) ,
    # now do last batch
    if len(recordBatch) > 0:
        data = u''.join( recordBatch )
        resp = solrConnection.postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data )
    if bibCount > 0:
        print "\n[%s] done updating bibs, now committing" % time.ctime()
        try:
            if commitNonblocking:
                solrConnection.commitNonblocking()
            else:
                solrConnection.commit()
        except IOError:
            print "Connection reset when talking to Solr, skipping this commit and sleeping 10 sec."
            time.sleep(10)
        print "[%s] done committing" % time.ctime()
    else:
        print "[%s] no bibs updated, exiting" % time.ctime()
    return bibCount


if __name__ == '__main__':

    processFilesInDirectory(HORIZON_BASE_DIR)
    # finally, do an optimize here
    if DO_OPTIMIZE:
        print "starting final optimize"
        solrConnection.optimize()    # csdebug
        facetWarmer.warmFacets()
    