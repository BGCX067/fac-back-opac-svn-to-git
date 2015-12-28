"""
Various classes and functions for working with MARC records.
"""

from java.io import *
from java.net import *
import time

class MarcExtractor:
    """extracts parts of a MARC record based upon an extraction string    
    """
    # TODO: document extraction string syntax
    def __init__(self, marcRecord):
        if type( marcRecord ) == type(""): marcRecord = eval(marcRecord)
        self.marcRecord = marcRecord
    def extract(self, extractString, dedupe=1, stripTrailingPunctuation = 1, trailingPunctuationToStrip = [".", ","], separator = " " ):
        # TODO: figure out if using a dict here for ret (instead of a list) would make 
        # things faster/easier to deal with duplicates
        ret = []
        thingsToExtract = [x.strip() for x in extractString.split(",") ]
        for extractStringOn in thingsToExtract:
            if extractStringOn.find("$") > -1:
                tag, subfields = extractStringOn.split("$")
                if self.marcRecord.has_key(tag):
                    for fieldOn in self.marcRecord[tag]:
                        subfieldsToAdd = []
                        for subfieldOn in subfields:
                            if fieldOn.has_key( "%s" % subfieldOn ):
                                sfOn = fieldOn[subfieldOn].strip()
                                if stripTrailingPunctuation and (len(sfOn) > 0) and (sfOn[-1] in trailingPunctuationToStrip):
                                    sfOn = sfOn[:-1]
                                subfieldsToAdd.append( sfOn )
                        if len(subfieldsToAdd) > 0:
                            if not dedupe:
                                ret.append( separator.join( subfieldsToAdd) )
                            else:
                                toAdd = separator.join(subfieldsToAdd)
                                if toAdd not in ret:
                                    ret.append( toAdd )
            elif extractStringOn.find("/") > -1:
                tag,positions = extractStringOn.split("/")
                if self.marcRecord.has_key(tag):
                    for fieldOn in self.marcRecord[tag]:
                        splitted = [int(x) for x in positions.split(":")]
                        if len(splitted) == 1:
                            try: 
                                ret.append( fieldOn[ splitted[0] ] )
                            except IndexError:
                                pass    # just ignore
                        elif len(splitted) == 2:
                            try: 
                                ret.append( fieldOn[ splitted[0] : splitted[1] ] )
                            except IndexError:
                                pass
        return ret
     

    