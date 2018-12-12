import struct
import sys
from google.protobuf.message import Message
from . import googleplay_pb2

VERSION = sys.version_info[0]

def isIterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def isProtobuf(obj):
    """Really bad workaround to check if an object is an
    instance of a protobuf message"""
    return hasattr(obj, "MergeFrom")

def parseProtobufObj(obj):
    output = {}
    for (fd, value) in obj.ListFields():
        key = fd.name
        if isProtobuf(value):
            if not isIterable(value):
                output.update({key: parseProtobufObj(value)})
            else:
                output.update({
                    key: [parseProtobufObj(i) for i in value]
                })
        else:
            output.update({key: value})
    return output

def readInt(byteArray, start):
    """Read the byte array, starting from *start* position,
    as an 32-bit unsigned integer"""
    return struct.unpack("!L", byteArray[start:][0:4])[0]


def toBigInt(byteArray):
    """Convert the byte array to a BigInteger"""
    array = byteArray[::-1]  # reverse array
    out = 0
    for key, value in enumerate(array):
        if VERSION == 3:
            decoded = struct.unpack("B", bytes([value]))[0]
        else:
            decoded = struct.unpack("B", value)[0]
        out = out | decoded << key * 8
    return out

def hasPrefetch(obj):
    try:
        return len(obj.preFetch) > 0
    except ValueError:
        return False

def hasListResponse(obj):
    try:
        return obj.HasField('listResponse')
    except ValueError:
        return False

def hasSearchResponse(obj):
    try:
        return obj.HasField('searchResponse')
    except ValueError:
        return False

def hasCluster(obj):
    try:
        return obj.HasField('cluster')
    except ValueError:
        return False

def hasTosContent(tocResponse):
    try:
        return tocResponse.HasField('tosContent')
    except ValueError:
        return False

def hasTosToken(tocResponse):
    try:
        return tocResponse.HasField('tosToken')
    except ValueError:
        return False

def hasCookie(tocResponse):
    try:
        return tocResponse.HasField('cookie')
    except ValueError:
        return False

def hasDoc(obj):
    # doc an be a single object or a
    # RepeatedComposite object
    try:
        existance = obj.HasField('doc')
    except ValueError:
        try:
            existance = len(obj.doc) > 0
        except TypeError:
            existance = False

    return existance
