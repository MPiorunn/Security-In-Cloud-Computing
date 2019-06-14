import os, random

from charm.core.math.pairing import hashPair as h
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction


class Alice:
    def __init__(self, group):
        self.group = group
        self.generator = group.random(G1)
        self.sk = self.group.random(ZR)
        self.pk = self.generator ** self.sk

        self.A0, self.A1 = [self.group.random(G1) for i in range(2)]
        self.B0, self.B1 = [self.group.random(G1) for i in range(2)]

        self.encryption_keys = [self.A0, self.A1]
        self.message = [self.B0, self.B1]

        self.random = [self.group.random(ZR) for i in range(2)]
        self.keys = [self.A0, self.A1]

    def getPublicKey(self):
        return self.generator, self.pk

    def generateRandom(self):
        return [self.generator ** self.random[i] for i in range(2)]

    def mask(self, set):
        mask = [set ** (1 / self.random[i]) for i in range(2)]
        return [mask[i] * self.message[i] for i in range(2)]


class Bob:
    def __init__(self, group, generator, pk):
        self.group = group
        self.generator = generator
        self.pk = pk
        self.C0, self.C1 = [os.urandom(128) for i in range(2)]

    def returnC0C1(self):
        return self.C0, self.C1

    def computeSet(self, random, key):
        self.key = key
        self.alpha = self.group.random(ZR)
        return random[key] ** self.alpha

    def computeMessage(self, mask):
        self.message = mask[self.key] / (self.generator ** self.alpha)
        return self.message

    def decrypt(self, table, key, alice_keys):
        for i, t in enumerate(table):
            try:
                a = decrypt(alice_keys[key], self.message, t)
                if a == self.C1:
                    print("Result = 1")
                elif a == self.C0:
                    print("Result = 0")
            except:
                pass


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

alice = Alice(group)
generator, pk = alice.getPublicKey()
bob = Bob(group, generator, pk)

C0, C1 = bob.returnC0C1()
alice_key = 1
bob_key = 0

garbledCircuit = [
    encrypt(alice.A0, alice.B0, C0),
    encrypt(alice.A0, alice.B1, C0),
    encrypt(alice.A1, alice.B0, C0),
    encrypt(alice.A1, alice.B1, C1)
]
# shuffle circuit
random.shuffle(garbledCircuit)
random = alice.generateRandom()

# Oblivious transfer
set = bob.computeSet(random, alice_key)

# mask messages
mask = alice.mask(set)

message = bob.computeMessage(mask)  #

bob.decrypt(garbledCircuit, bob_key, alice.keys)
