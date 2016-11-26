import binascii
import hashlib
import logging


def hashBuffer(b):
    shaAccum = hashlib.sha1()
    shaAccum.update(b)
    return binascii.b2a_base64(shaAccum.digest()).strip()


def hashFile(fileName, offset=0):
    chunk_size = 1024
    shaAccum = hashlib.sha1()
    try:
        with open(fileName, "rb") as f:
            f.seek(offset)
            byte = f.read(chunk_size)
            while byte:  # pragma: no branch
                shaAccum.update(byte)
                byte = f.read(chunk_size)
    except IOError:
        log = logging.getLogger(__name__)
        log.error("Cannot Hash '%s'", fileName)
        return ''
    return binascii.b2a_base64(shaAccum.digest()).strip()
