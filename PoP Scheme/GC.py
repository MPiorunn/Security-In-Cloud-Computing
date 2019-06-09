import os

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

    def get_public_data(self):
        return self.generator, self.pk

    def generate_random(self):
        return [self.generator ** self.random[i] for i in range(2)]

    def masquarade(self, _set):
        masqueraded = [_set ** (1 / self.random[i]) for i in range(2)]
        return [masqueraded[i] * self.message[i] for i in range(2)]


class Bob:
    def __init__(self, group, generator, pk):
        self.group = group
        self.generator = generator
        self.pk = pk
        self.C0, self.C1 = [os.urandom(128) for i in range(2)]

    def returnC0C1(self):
        return self.C0, self.C1

    def compute_set(self, random, key):
        self.key = key
        self.alpha = self.group.random(ZR)
        _set = random[key] ** self.alpha
        return _set

    def compute_message(self, masqueraded):
        self.message = masqueraded[self.key] / (self.generator ** self.alpha)
        return self.message

    def decrypt(self, Table, key, alice_keys):
        for i, t in enumerate(Table):
            try:
                a = dec(alice_keys[key], self.message, t)
                if a == self.C1:
                    print("C1")
                elif a == self.C0:
                    print("C0")
            except:
                pass


def enc(k1, k2, msg):
    a1 = SymmetricCryptoAbstraction(h(k1))
    a2 = SymmetricCryptoAbstraction(h(k2))
    c = a2.encrypt(a1.encrypt(msg))
    return c


def dec(k1, k2, ctx):
    a1 = SymmetricCryptoAbstraction(h(k1))
    a2 = SymmetricCryptoAbstraction(h(k2))
    expansion_ratio = a1.decrypt((a2.decrypt(ctx)).decode("utf-8"))
    return expansion_ratio


def main():
    group = PairingGroup('SS512')

    alice = Alice(group)
    generator, pk = alice.get_public_data()
    bob = Bob(group, generator, pk)

    C0, C1 = bob.returnC0C1()
    Table = [
        enc(alice.A0, alice.B0, C0),
        enc(alice.A0, alice.B1, C0),
        enc(alice.A1, alice.B0, C0),
        enc(alice.A1, alice.B1, C1)
    ]

    # OT
    random = alice.generate_random()
    alice_key = 1
    _set = bob.compute_set(random, alice_key)
    masqueraded = alice.masquarade(_set)
    message = bob.compute_message(masqueraded)  # ?

    bob_key = 1
    bob.decrypt(Table, bob_key, alice.keys)


if __name__ == "__main__":
    main()
