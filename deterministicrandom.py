#!/usr/bin/python

"""
Deterministic uniform random numbers, with 32-bits of precision.
We provide random access given a particular key.

NOTE:
    * We use pyhash, a Python-wrapped C implementation of murmurhash 2. We
    use murmur2_neutral_32, which is supposed to produce identical results
    regardless of block alignment and machine-endianess, albeit slower
    that the other murmurhash 2 implementations.
    Use the SVN version of pyhash:
        http://code.google.com/p/pyfasthash/source/checkout

WARNING:
    * This is random access to an RNG. Instead of using a pseudo-RNG
    as such (which might be slow for random access), we use hashing to
    provide no-memory random access to random numbers. To test the
    randomness of this stream, use the following command:
        ./deterministicrandom.py -s | dieharder -g 200 -a

    * We might not have deterministic results across machine architectures
    and endianess. We haven't tested that the hash function is truly
    deterministic. Also, converting the object to a string before
    hashing it might give different results depending upon the machine
    and Python version.

TODO:
    * Make sure that we get a 4-byte value from murmurhash!!!
    * Construct float value from 64-bits, not 32-bits.
"""

import sys
import pyhash

# We expect the hash to be 4 bytes long
HASH_BYTES = 4
MAX_HASH_VALUE = 2**(8*HASH_BYTES)

_hasher = pyhash.murmur2_neutral_32()

def deterministicrandom(x):
    """
    Convert x (any Python value) to a deterministic uniform random number
    in [0, 1), with 32-bits of precision.

    TODO: Construct float value from 64-bits, not 32-bits.
    """

    i = hash_value(x)

    r = 1.0 * i / MAX_HASH_VALUE
    return r

def hash_value(x):
    """
    TODO: Make sure that we get a 4-byte value!!!
    """
    i = _hasher(`x`)
#    assert sys.sizeof(i) == HASH_BYTES
    assert i >= 0 and i < MAX_HASH_VALUE
    return i

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--stream", action="store_true", default=False, dest="stream", help="stream random numbers to stdout")
    (options, args) = parser.parse_args()
    assert len(args) == 0

    import os
    import struct
    # Make sure that packing to a struct of type L (standard unsigned long) is
    # 4 bytes, which is the length of the murmurhash output. (Actually,
    # we don't sanity check murmurhash length :( .)
    assert len(struct.unpack("cccc", struct.pack("=L", hash_value(0)))) == HASH_BYTES

    if not options.stream:
        array = [deterministicrandom(i) for i in range(1000)]
        import numpy
        print "mean (should be 0.5) = ", numpy.mean(array)

        print >> sys.stderr, "Writing 500000 bytes of random output to randomoutput.bin"
        f = open("randomoutput.bin", "wb")
        for i in range(1250000):
            f.write(struct.pack("=L", hash_value(i)))
        os.system("ent randomoutput.bin")
    else:
        i = 0
        import common.stats
        while 1:
            sys.stdout.write(struct.pack("=L", hash_value(i)))
            i += 1
#            if i % 1000000 == 0: print >> sys.stderr, i, common.stats.stats()
