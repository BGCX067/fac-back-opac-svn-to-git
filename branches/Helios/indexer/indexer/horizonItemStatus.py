"""
Functionality for extracting item statuses from Horizon for use in indexing.
"""
from java.lang import *
from java.io import *
from java.sql import *
from java.util import *

import sys, urllib, time

from loadPropsFile import *

from config.solr import *
import solrConnection

#1. get connection to the database

props = loadPropsFile("config/ILSConn.properties")

# TODO: decide if this should use splcommons.HorizonConn instead
dbType = props['db.type']
 
if dbType != "sybase":
    print "database type %s not yet supported." % dbType
    sys.exit(1)
else:
    connString = "jdbc:jtds:%(db.type)s://%(db.server)s:%(db.port)s/%(db.name)s" % props
    Class.forName( props['db.driver'] ).newInstance()
    conn = DriverManager.getConnection( connString, props['db.user'], props['db.password'] )


def updateSolrRecordAvailability( bibNum, availableLocations = [], doPost =1 ):
    """this function updates an already-indexed record from Solr with new location information.
    It does this by grabbing the record in python format, evaling it as a python object, updating
    that one attribute and then re-serializing it as XML.  WHEW/UGH!  The method is so convoluted
    because Lucene does not allow you to update just one field in an indexed document -- you must
    delete the whole document and re-add it.
    """
    urlToGet = "%s?q=bib_num:%s&wt=python" % ( SOLR_QUERY_URL, bibNum )
    # TODO: better error handling
    try:
        u = urllib.urlopen(urlToGet)
        data = u.read()
        u.close()
    except IOError:
        # connections sometimes reset; sleep a little while and try again -- if fails again, bomb out with error.
        print "IOError while trying to get URL %s" % urlToGet
        time.sleep(1.0)
        u = urllib.urlopen(urlToGet)
        data = u.read()
        u.close()
    try:
        evData = eval(data)
    except:
        print "error while trying to eval record for %s" % bibNum 
    try:
        docOn = evData['response']['docs'][0]
    except:    # some error was reached; just toss it back
        return data    
    docOn['available'] = availableLocations
    
    # now serialize the updated doc as XML
    ret = u""
    for kOn in docOn.keys():
        valueOn = docOn[kOn]
        if type(valueOn) == type([]):
            for subvalueOn in valueOn:
                sv = str(subvalueOn).replace("&", "&amp;").replace("<", "&amp;lt;").replace(">", "&amp;gt;")
                ret  += u"""<field name="%s">%s</field>""" % ( kOn, sv )
        else:
            val = str(valueOn).replace("&", "&amp;").replace("<", "&amp;lt;").replace(">", "&amp;gt;")
            ret += u"""<field name="%s">%s</field>""" % ( kOn, val )
    
    # now POST update if required
    if doPost:
        resp = solrConnection.postURL( SOLR_UPDATE_URL, "<add><doc>%s</doc></add>" % ret )
        return resp
    else:
        return "<doc>%s</doc>" % ret

def availableAt( arg  ):
    """returns either a list of locations where an item is checked in
    or a dictionary where the keys are bib #'s and the values are lists of locations where
    that bib is checked in at, depending upon whether it is given a number or a list of numbers.
    If update == 1, it also updates the helios_item_status table to keep it in sync with your indexing job.
    """
    
    if type(arg) == type([]):
        ret ={}
        ps = conn.prepareStatement( """select distinct location, item# from item where bib#=? and item_status = 'i'""")
        for bibOn in arg:
            ps.setInt(1, int(bibOn) )
            rs = ps.executeQuery()
            _locs = []
            _itemNums = []
            while rs.next():
                _locs.append( "%s" % rs.getString(1) )
                _itemNums.append( rs.getInt(2) )
            rs.close()
            ret[bibOn] = _locs
        ps.close()
        return ret     
    else:
        ret = []
        _itemNums = []
        locQuery = """select distinct location, item# from item where bib#=%s and item_status = 'i'""" % arg
        stmt = conn.createStatement()
        rs = stmt.executeQuery( locQuery )
        
        while rs.next():
            ret.append( "%s" % rs.getString(1) )
            _itemNums.append( rs.getInt(2) )
        rs.close()
        stmt.close()
        return ret

def deleteFromIndexQueue( bib_num ):
    """deletes a given bib# from the helios_index_queue.  Should be called when appropriate if not
    using doDelete = 1 with getChangedBibs"""
    delQuery = "delete from helios_index_queue where bib# = %s" % bib_num
    stmt = conn.createStatement()
    result = stmt.execute( delQuery )
    stmt.close()
    return

def reindexRecordsModifiedYesterday():
    stmt = conn.createStatement()
    rs = stmt.executeQuery( "select datediff(dd,'1/1/1970',getdate())" )
    rs.next()
    today = int( rs.getInt(1) )
    yesterday = today - 1
    reindexRecordsModifiedOn(yesterday)
    try:
        stmt.close()
        rs.close()
    except:
        pass

def testDBConn():
    stmt = conn.createStatement()
    rs = stmt.executeQuery("select * from matham")
    if rs.next():
        print "rs is %s" % rs
        print rs.getString(1)
    else:
        print "no results"
    rs.close()
    

def reindexRecordsModifiedOn( sybdate ):
    """puts all bibs that had a status update date == sybdate in the helios_index_queue table."""
    recordsQuery = """select distinct bib# from item where last_status_update_date = %s""" % sybdate
    stmt = conn.createStatement()
    updStmt = conn.createStatement()
    rs = stmt.executeQuery( recordsQuery )
    count = 0
    while rs.next():
        count +=1
        bibOn = rs.getInt(1)
        insertQuery = """insert helios_index_queue values (%s)""" % bibOn
        print "!",
        result = updStmt.execute(insertQuery)
    print "inserted %s records" % count
    try:
        rs.close()
        stmt.close()
        updStmt.close()
    except:
        pass
    
     

def getChangedBibs(doDelete = 1):
    """this function returns all the bibs that are waiting for reindexing in helios_index_queue
        and then clears that table (if doDelete ==1) """
    
    changedBibsQuery = "select * from helios_index_queue"
    
    conn.setAutoCommit(0)
    stmt = conn.createStatement()
    rs = stmt.executeQuery( changedBibsQuery )
    ret = []
    while rs.next():
        ret.append( rs.getInt(1) )
    if doDelete:
        delQuery = "delete from helios_index_queue"
        try:
            result = stmt.execute(delQuery)
            conn.commit()
        except:
            print "exception! rolling back transaction"
            conn.rollback()
    else:
        conn.commit()
    conn.setAutoCommit(1)
    try:
        rs.close()
        stmt.close()
    except:
        pass
    return ret

def cleanup():
    conn.close()
    