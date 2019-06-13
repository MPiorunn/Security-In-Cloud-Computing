from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
import time

class ELGamal:
    def __init__(self, group, generator):
        self.group = group
        self.generator = generator

    def encrypt(self, expansion_ratio, h):
        y = self.group.random(ZR)
        return self.generator ** y, h ** y * expansion_ratio

    def decrypt(self, C, x):
        return C[1] / (C[0] ** x)


class Alice:
    def __init__(self, group):
        self.group = group
        self.secret_key = self.group.random(ZR)
        self.generator = self.group.random(G1)
        self.public_key = self.generator ** self.secret_key

    def generatePublicKey(self):
        return self.generator, self.public_key

    def PrepareMessages(self, B, m0, m1, elgamal):
        k0 = self.group.hash(self.group.serialize(B ** self.secret_key))
        k1 = self.group.hash(self.group.serialize((B / self.public_key) ** self.secret_key))
        h0 = self.generator ** k0
        h1 = self.generator ** k1
        return elgamal.encrypt(m0, h0), elgamal.encrypt(m1, h1)


class Bob:
    def __init__(self, group, generator, public_key):
        self.group = group
        self.generator = generator
        self.public_key = public_key
        # which message Bob wants to receive
        self.c = 0
        self.b = self.group.random(ZR)

    def mask(self):
        if self.c == 0:
            return self.generator ** self.b
        elif self.c == 1:
            return self.public_key * self.generator ** self.b
        else:
            return None

    def decode(self, ciphers, elgamal):
        k = self.group.hash(self.group.serialize(self.public_key ** self.b))
        return elgamal.decrypt(ciphers[self.c], k)


group = PairingGroup('SS512')

alice = Alice(group)
generator, public_key = alice.generatePublicKey()

elgamal = ELGamal(group, generator)

bob = Bob(group, generator, public_key)
start = time.time()

B = bob.mask()
if B is not None:
    m0 = group.random(G1)
    m1 = group.random(G1)
    ciphers = alice.PrepareMessages(B, m0, m1, elgamal)
    decrypted = bob.decode(ciphers, elgamal)
    end = time.time()
    if m0 == decrypted:
        print("Decrypted message 1")
    elif m1 == decrypted:
        print("Decrypted message 2")
    else:
        print("None of two messages were decrypted, error")
    print("Execution time {}s".format(end - start))
