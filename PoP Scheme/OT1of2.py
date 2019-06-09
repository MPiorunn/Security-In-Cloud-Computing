#!/usr/bin/python3

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1


class ELGamal:
    def __init__(self, group, generator):
        self.group = group
        self.generator = generator

    def encrypt(self, expansion_ratio, h):
        y = self.group.random(ZR)
        return self.generator ** y, h ** y * expansion_ratio

    def decrypt(self, C, x):
        return C[1] / (C[0] ** x)


class Sender:
    def __init__(self, group):
        self.group = group
        self.secret_key = self.group.random(ZR)
        self.generator = self.group.random(G1)
        self.public_key = self.generator ** self.secret_key

    def GetPublicKey(self):
        return self.generator, self.public_key

    def PrepareMessages(self, B, M1, M2, elgamal):
        k0 = self.group.hash(self.group.serialize(B ** self.secret_key))
        k1 = self.group.hash(self.group.serialize((B / self.public_key) ** self.secret_key))
        h0 = self.generator ** k0
        h1 = self.generator ** k1
        return elgamal.encrypt(M1, h0), elgamal.encrypt(M2, h1)


class Receiver:
    def __init__(self, group, generator, public_key, c):
        self.group = group
        self.generator = generator
        self.public_key = public_key
        self.c = c
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


def main():
    group = PairingGroup('SS512')
    sender = Sender(group)
    generator, public_key = sender.GetPublicKey()
    elgamal = ELGamal(group, generator)

    c = 0  # 0=>M1   1=>M2
    receiver = Receiver(group, generator, public_key, c)
    B = receiver.mask()
    if B is not None:
        M1 = group.random(G1)
        M2 = group.random(G1)
        ciphers = sender.PrepareMessages(B, M1, M2, elgamal)
        decrypted = receiver.decode(ciphers, elgamal)
        if M1 == decrypted:
            print("M1")
        elif M2 == decrypted:
            print("M2")
        else:
            print("Error")


if __name__ == "__main__":
    main()
