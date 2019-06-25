import os
import random
import time

from charm.core.math.pairing import hashPair as h
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction


class Alice:
    def __init__(self, group, bit):
        self.group = group
        self.generator = group.random(G1)
        self.sk = self.group.random(ZR)
        self.pk = self.generator ** self.sk

        self.kx0, self.kx1 = [self.group.random(G1) for i in range(2)]
        self.ky0, self.ky1 = [self.group.random(G1) for i in range(2)]
        self.kz0, self.kz1 = [os.urandom(128) for i in range(2)]

        # Encryption keys for each "AND" input
        self.keys = [self.kx0, self.kx1]

        self.message = [self.ky0, self.ky1]

        self.random = [self.group.random(ZR) for i in range(2)]

        self.bit = bit

    def createGCT(self):
        gct = [
            # Ekx0(Eky0(kz0))
            encrypt(self.kx0, self.ky0, self.kz0),

            # Ekx0(Eky1(kz0))
            encrypt(self.kx0, self.ky1, self.kz0),

            # Ekx1(Eky0(kz0))
            encrypt(self.kx1, self.ky0, self.kz0),

            # Ekx1(Eky1(kz1))
            encrypt(self.kx1, self.ky1, self.kz1)
        ]
        return gct

    def getPublicKey(self):
        return self.generator, self.pk

    def generateRandomMessages(self):
        return [self.generator ** self.random[i] for i in range(2)]

    def mask(self, s):
        mask = [s ** (1 / self.random[i]) for i in range(2)]
        return [mask[i] * self.message[i] for i in range(2)]

    def getFirstKey(self):
        return self.kx0 if self.bit == 0 else self.kx1


class Bob:
    def __init__(self, group, generator, pk, bit):
        self.group = group
        self.generator = generator
        self.pk = pk
        self.bit = bit

    def setFirstKey(self, key):
        self.firstKey = key

    def generateS(self, random):
        self.alpha = self.group.random(ZR)
        return random[self.bit] ** self.alpha

    def computeSecondKey(self, mask):
        self.secondKey = mask[self.bit] / (self.generator ** self.alpha)

    def decrypt(self, table):
        ciphers = []
        for i, t in enumerate(table):
            try:
                ciphers.append(decrypt(self.firstKey, self.secondKey, t))
            except:
                pass

        return ciphers


def encrypt(k1, k2, msg):
    a1 = SymmetricCryptoAbstraction(h(k1))
    a2 = SymmetricCryptoAbstraction(h(k2))
    c = a2.encrypt(a1.encrypt(msg))
    return c


def decrypt(k1, k2, ctx):
    a1 = SymmetricCryptoAbstraction(h(k1))
    a2 = SymmetricCryptoAbstraction(h(k2))
    expansion_ratio = a1.decrypt((a2.decrypt(ctx)).decode("utf-8"))
    return expansion_ratio


group = PairingGroup('SS512')
alice_bit = 1
bob_bit = 1

start = time.time()
alice = Alice(group, alice_bit)
generator, pk = alice.getPublicKey()
bob = Bob(group, generator, pk, bob_bit)

# Prepare Garbled Computation Table (GCT)
garbledCircuit = alice.createGCT()

# shuffle circuit so the order is random
random.shuffle(garbledCircuit)

# send first encryption key to Bob
kxb = alice.getFirstKey()
bob.setFirstKey(kxb)

# Oblivious transfer

# Alice generates x0 , x1
random = alice.generateRandomMessages()

# Bob sends s which is (xb - k^e) mod N
s = bob.generateS(random)

maskedSecondKey = alice.mask(s)

bob.computeSecondKey(maskedSecondKey)

result = bob.decrypt(garbledCircuit)

if alice.kz0 in result:
    end = time.time()
    print("Result = 0")
    print("Execution time {}".format(end - start))
elif alice.kz1 in result:
    end = time.time()
    print("Result = 1")
    print("Execution time {}".format(end - start))
else:
    print("Wrong protocol execution")
