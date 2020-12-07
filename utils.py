from codecs import getdecoder
from codecs import getencoder


encoder = getdecoder("hex")
decoder = getencoder("hex")


def strxor(a, b):
    mlen = min(len(a), len(b))
    a, b, xor = bytearray(a), bytearray(b), bytearray(mlen)
    for i in range(mlen):
        xor[i] = a[i] ^ b[i]
    return bytes(xor)


def hexdecode(data):
    return encoder(data)[0]


def hexencode(data):
    return decoder(data)[0].decode("ascii").upper()
