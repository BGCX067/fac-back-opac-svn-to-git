"""
Utilities for preparing records to send to Solr
"""
from java.io import *
from java.net import *
from org.marc4j import *
from org.marc4j.converter.impl import *
from loadPropsFile import *
from marcExtractor import *
from processors import *
import marcIndexingUtils
import time

class recordForSolr:
    """takes a marc record and processes it using the configurations specified in 
    indexer.properties.  Returns an object with all indexed fields as object attributes.  
    The serialize() method converts the object to a Solr record.
    If you pass in a propsObject, it does not have to reload the .properties file for every record you create. 
    """
    def __init__(self, marcRecord, anselUnicodeConverter = None, accession = None, profile=0, propsObject = None, indexerProperties="config/indexer.properties"):
        start = time.time()
        self._marcRecordToDictTime = 0
        self._extractionTime = 0
        self._extractorCreateTime = 0
        self._extractMethodTime = 0
        if profile:
            self._marcRecordToDictProfiling = {}
        
        if anselUnicodeConverter is None: 
            print "creating ansel -> unicode converter"    # csdebug
            anselUnicodeConverter = AnselToUnicode()
        if profile:
            record, _perfData = marcIndexingUtils.marcRecordToDict( marcRecord, anselUnicodeConverter )
            self._marcRecordToDictProfiling = _perfData
        else:
            record = marcIndexingUtils.marcRecordToDict( marcRecord, anselUnicodeConverter )
        self._marcRecordToDictTime = time.time() - start
        
        start = time.time()
        if not propsObject:
            config = loadPropsFile(indexerProperties)
        else:
            config = propsObject
        extractor = MarcExtractor( record )
        self._extractorCreateTime = (time.time() - start)
        
        # TODO: decide if this should be turn-offable or not
        self.marc_record = str( record )
        
        fieldsToDo = [x.strip() for x in config['active.fields'].split(",")]
        _processors = __import__('processors', {},{},[''])
        for fieldOn in fieldsToDo:
            start = time.time()
            processorNameOn = config.get( "%s.processor" % fieldOn, "standardProcessor" )
            marcMapOn = config.get("%s.marcMap" % fieldOn, None)
            # do processing
            if processorNameOn == "standardProcessor":    
                # then just use the MARC extractor
                separatorOn = config.get("%s.marcMap.separator" % fieldOn, " ")
                stripTrailingCommas = int( config.get("%s.stripTrailingCommas" % fieldOn, "0") )
                if stripTrailingCommas:
                    extractMethodStart = time.time()
                    processedResult = extractor.extract( marcMapOn, separator = separatorOn, trailingPunctuationToStrip = [","], stripTrailingPunctuation = 1 )
                    self._extractMethodTime += ( time.time() - extractMethodStart )
                else:
                    stripTrailingPunctuation = int( config.get("%s.stripTrailingPunctuation" % fieldOn, "0") )
                    try:
                        extractMethodStart = time.time()
                        processedResult = extractor.extract( marcMapOn, separator = separatorOn, stripTrailingPunctuation = stripTrailingPunctuation )
                        self._extractMethodTime += ( time.time() - extractMethodStart )
                    except AttributeError:
                        print "You do not have a correct marc mapping set up for field %s" % fieldOn
                if ((processedResult == None) or len(processedResult) == 0) and config.has_key("%s.marcMap.lastResort" % fieldOn ):
                    marcMapOn = config.get("%s.marcMap.lastResort" % fieldOn, None)
                    extractMethodStart = time.time()
                    processedResult = extractor.extract( marcMapOn, separator = separatorOn )
                    self._extractMethodTime += ( time.time() - extractMethodStart )
            else:
                # get and run custom processor
                processorOn = getattr( _processors, processorNameOn )    
                processedResult = processorOn( record, marcMap=marcMapOn, extractor=extractor )
            # do post-processing based upon type
            typeOn = config.get("%s.type" % fieldOn, "multi")
            if typeOn == "single" and ( type(processedResult) == type([])) and len(processedResult) > 0:
                postProcessedResult = processedResult[0]
            elif typeOn == "singleTranslation":
                if( type(processedResult) == type([]) ):
                    if len(processedResult) >= 1:
                        processedResult = processedResult[0]
                    else:
                        processedResult = None
                translationMapName = config.get("%s.translationMap" % fieldOn, None)
                if translationMapName is not None:
                    _translationMapModule = __import__( "config.codes" , {},{},[''] )
                    _translationMap = getattr( _translationMapModule, translationMapName)
                    postProcessedResult = _translationMap.get( processedResult, None)
            else:
                postProcessedResult = processedResult
            # deal with stripWhitespace after all other text manipulations
            stripWhitespace = int( config.get("%s.stripWhitespace" % fieldOn, "0") )
            if stripWhitespace:
                if type( postProcessedResult ) == type(""):
                    postProcessedResult = postProcessedResult.strip()
                elif type( postProcessedResult) == type([]):
                    postProcessedResult = [x.strip() for x in postProcessedResult]
            # FINALLY, set own attribute
            if postProcessedResult is not None and len(postProcessedResult) > 0:
                setattr( self, fieldOn, postProcessedResult )
            self._extractionTime += ( time.time() - start )
    def __str__(self):
        import pprint
        ret = []
        for attr in dir(self):
            ret.append( "%s -> %s" % ( attr, pprint.pformat( getattr(self, attr) ) ) )
        return "\n".join(ret)
    def serialize(self):
        out = "" 
        attrs = [ x for x in self.__dict__.keys() if not x.startswith("_") ]
        for attrOn in attrs:
            value = getattr( self, attrOn )
            if type(value) == type( [] ):
                for subvalueOn in value: 
                    subvalueOn = subvalueOn.replace("&", "&amp;").replace("<", "&amp;lt;").replace(">", "&amp;gt;") 
                    out += u"""<field name="%s">%s</field>""" % ( attrOn, subvalueOn)
            else:
                field = getattr(self, attrOn)
                if field: 
                    field = field.replace("&", "&amp;").replace("<", "&amp;lt;").replace(">", "&amp;gt;" ) 
                    out += u"""<field name="%s">%s</field>""" % ( attrOn, field )
                else: 
                    print "field %s was None!" % attrOn    
        return u"<doc>%s</doc>" % out
         
