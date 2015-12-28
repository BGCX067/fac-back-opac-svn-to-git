import struct
import socket
import types
from helios.config import *
import helios.logger as logger

# following functions are used by Helios' ability to determine what library someone is at
# based upon their IP address. They are
# based heavily on http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66517
# note that this may produce weird results on diff't endian
# machines???
def IPAddressToInt( ip ) :
    """converts a dotted quad IP address to its Long integer value"""
    return struct.unpack("!L", socket.inet_aton( ip ) )[0]   
    
def intToIPAddress( aLong ):
    """converts a long integer to its corresponding IP address"""
    return socket.inet_ntoa( struct.pack("!L", aLong ) )
    
def parseLocationIPAddressRanges( ranges ):
    addressLocationMap = {}
    for k,v in ranges.iteritems():
        if k in LOCATION_NAMES.keys():
            if type(v) in types.StringTypes:
                # individual IP address - - just put in key/value pair
                asLong = IPAddressToInt( v )
                addressLocationMap[asLong] = k
            elif type(v) == types.TupleType:
                logger.debug( "on %s" %  v )
                startAsLong, endAsLong =  IPAddressToInt( v[0] ), IPAddressToInt( v[1] )
                if startAsLong < endAsLong:
                    logger.debug( "adding %s addresses..." % ( endAsLong -startAsLong) )
                    for i in range(startAsLong, endAsLong+1): # NB fencepost
                        addressLocationMap[i] = k
            elif type(v) == types.ListType:
                for x in v:
                    if type(x) == types.TupleType:
                        logger.debug(  "on\n%s" % v )
                        startAsLong, endAsLong = IPAddressToInt(x[0]), IPAddressToInt(x[1])
                        if startAsLong < endAsLong:
                            logger.debug( "adding %s addresses" % ( endAsLong -startAsLong) )
                            for i in range(startAsLong, endAsLong+1): # NB fencepost
                                addressLocationMap[i] = k
    return addressLocationMap                                
    
    
def doPagination( page, totalFound, numPerPage, isZeroIndexed = True ):
    """creates the pagination object used by various Helios views"""
    ret = []
    if isZeroIndexed:
        if page < 5:
            startPage = 0
        else:
            startPage = page - 5
        if totalFound % numPerPage:    
            lastPage = (totalFound // numPerPage) + 1
        else:
            lastPage = (totalFound // numPerPage)
        endPage = min( lastPage, page + 5)
        for i in range( startPage, endPage):
            ret.append( { 'selected' : (i == page) , 'start' : ( i * numPerPage) + 1, 'end' : min( totalFound, ( i + 1) * numPerPage), 'page' : i, 'pageLabel' : i+1 } )
        return {'pages' : ret , 'hasPrevious' : (page > 0), 'hasNext' : page < ( lastPage - 1 ), 'previousPage' : page-1, 'nextPage' : page+1 }
    else:    # 1 indexed (used by embedded HIP display)
        page = page + 1     # TODO: deal with this ugly 0be1 wart
        if page < 6:
            startPage = 1
        else:
            startPage = page - 5
        if totalFound % numPerPage:    
            lastPage = (totalFound // numPerPage) + 2
        else:
            lastPage = (totalFound // numPerPage) + 1
        endPage = min( lastPage, page + 5)
        logger.debug( "startPage is %s, endPage is %s, lastPage is %s, page is %s" % ( startPage, endPage, lastPage, page) )
        for i in range( startPage, endPage):
            ret.append( { 'selected' : (i == page) , 'start' : ( i * numPerPage) + 1, 'end' : min( totalFound, ( i + 1) * numPerPage), 'page' : i, 'pageLabel' : i } )
        return {'pages' : ret , 'hasPrevious' : (page > 1), 'hasNext' : page < ( lastPage - 1 ), 'previousPage' : page-1, 'nextPage' : page+1 }
    
        

