from struct import pack

from gost.gost28147 import addmod
from gost.gost28147 import block2ns
from gost.gost28147 import E
from gost.gost28147 import ns2block
from utils import hexdecode
from utils import hexencode
from utils import strxor


BLOCKSIZE = 32
iteration = 2

C2 = 32 * b'\x00'
C3 = hexdecode(b'ff00ffff000000ffff0000ff00ffff0000ff00ff00ff00ffff00ff00ff00ff00')
C4 = 32 * b'\x00'


def A(Y):
    y4, y3, y2, y1 = Y[0:8], Y[8:16], Y[16:24], Y[24:32]
    return b''.join((strxor(y1, y2), y4, y3, y2))


def P(Y):
    return bytearray((
        Y[0], Y[8], Y[16], Y[24], Y[1], Y[9], Y[17], Y[25], Y[2],
        Y[10], Y[18], Y[26], Y[3], Y[11], Y[19], Y[27], Y[4], Y[12],
        Y[20], Y[28], Y[5], Y[13], Y[21], Y[29], Y[6], Y[14], Y[22],
        Y[30], Y[7], Y[15], Y[23], Y[31],
    ))


def shuffle(Y):
    (y16, y15, y14, y13, y12, y11, y10, y9, y8, y7, y6, y5, y4, y3, y2, y1) = (
        Y[0:2], Y[2:4], Y[4:6], Y[6:8], Y[8:10], Y[10:12], Y[12:14],
        Y[14:16], Y[16:18], Y[18:20], Y[20:22], Y[22:24], Y[24:26],
        Y[26:28], Y[28:30], Y[30:32],
    )
    by1, by2, by3, by4, by13, by16, byx = (
        bytearray(y1), bytearray(y2), bytearray(y3), bytearray(y4),
        bytearray(y13), bytearray(y16), bytearray(2),
    )
    byx[0] = by1[0] ^ by2[0] ^ by3[0] ^ by4[0] ^ by13[0] ^ by16[0]
    byx[1] = by1[1] ^ by2[1] ^ by3[1] ^ by4[1] ^ by13[1] ^ by16[1]
    return b''.join((
        bytes(byx), y16, y15, y14, y13, y12, y11, y10, y9, y8, y7, y6, y5, y4, y3, y2
    ))


def f(H_in, m):
    global iteration
    print('--------H{0}--------'.format(iteration))
    print('Генерация ключей')
    U = H_in
    V = m
    W = strxor(H_in, m)
    K1 = P(W)
    print('K1 =', hexencode(K1))

    U = strxor(A(U), C2)
    V = A(A(V))
    W = strxor(U, V)
    K2 = P(W)
    print('K2 =', hexencode(K2))

    U = strxor(A(U), C3)
    V = A(A(V))
    W = strxor(U, V)
    K3 = P(W)
    print('K3 =', hexencode(K3))

    U = strxor(A(U), C4)
    V = A(A(V))
    W = strxor(U, V)
    K4 = P(W)
    print('K4 =', hexencode(K4))

    h4, h3, h2, h1 = H_in[0:8], H_in[8:16], H_in[16:24], H_in[24:32]
    s1 = ns2block(E(K1[::-1], block2ns(h1[::-1])))[::-1]
    s2 = ns2block(E(K2[::-1], block2ns(h2[::-1])))[::-1]
    s3 = ns2block(E(K3[::-1], block2ns(h3[::-1])))[::-1]
    s4 = ns2block(E(K4[::-1], block2ns(h4[::-1])))[::-1]
    s = b''.join((s4, s3, s2, s1))

    x = s
    for _ in range(12):
        x = shuffle(x)
    x = strxor(x, m)
    x = shuffle(x)
    x = strxor(H_in, x)
    for _ in range(61):
        x = shuffle(x)
    print('H_out = ', hexencode(x))
    iteration += 1
    print('--------------')
    return x


class GOST3411(object):
    def __init__(self, data=b''):
        self.data = data

    def __get_hash_bytes(self):
        print('M =', self.data)
        L = 0
        control_sum = 0
        h = 32 * b'\x00'
        print('H1 = ', hexencode(h))
        m = self.data
        for i in range(0, len(m), BLOCKSIZE):
            part = m[i:i + BLOCKSIZE][::-1]
            L += len(part) * 8
            control_sum = addmod(control_sum, int(hexencode(part), 16), 2 ** 256)
            if len(part) < BLOCKSIZE:
                part = b'\x00' * (BLOCKSIZE - len(part)) + part
            h = f(h, part)
        print('H(n + 2) = f(H(n+1), L)')
        h = f(h, 24 * b'\x00' + pack(">Q", L))

        control_sum = hex(control_sum)[2:].rstrip("L")
        if len(control_sum) % 2 != 0:
            control_sum = "0" + control_sum
        control_sum = hexdecode(control_sum)
        control_sum = b'\x00' * (BLOCKSIZE - len(control_sum)) + control_sum
        print('H(n + 3) = f(H(n+2), sum)')
        h = f(h, control_sum)
        return h[::-1]

    def hash(self):
        return hexencode(self.__get_hash_bytes())
