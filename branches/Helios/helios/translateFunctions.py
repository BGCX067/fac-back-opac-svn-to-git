from config import *
from marcConstants import *

def getLocationName(locationCode):
    return LOCATION_NAMES.get( locationCode.lower(), locationCode )

def getDeweyCenturyName( deweyCentury ):
    return DEWEY_CENTURY_MAP.get( str(deweyCentury), deweyCentury )

def getDeweyClassName( deweyClass ):
    return DEWEY_MAP.get( str(deweyClass), deweyClass )    

def getAuthorNameRightOrder( authorName ):
    if authorName.endswith(","): 
        authorName = authorName[:-1]
    names = [x.strip() for x in authorName.split(",")]

    if len(names) == 2:
        firstName, lastName = names[1], names[0]
        #if lastName.endswith("."):
        #    lastName = lastName[:-1]
        return "%s %s" % ( firstName, lastName ) 
    else:    # don't know what to do with it.  just return what we were given.
        return authorName