from charm.core.math.integer import isPrime, gcd, random, randomPrime, toInt
import time


class RSA:
    def __init__(self, secparam):

        # generate p,q
        while True:
            p, q = randomPrime(secparam), randomPrime(secparam)
            if isPrime(p) and isPrime(q) and p != q:
                N = p * q
                phi = (p - 1) * (q - 1)
                break

        # calculate private key and public key
        while True:
            e = random(phi)
            if not gcd(e, phi) == 1:
                continue
            d = e ** -1
            break

        # prepare public key
        self.pk = {'N': N, 'e': toInt(e)}

        # prepare private key
        self.sk = {'phi': phi, 'd': d, 'N': N}

    def keygen(self):
        return self.sk, self.pk


class Alice:
    def __init__(self, sk):
        self.sk = sk
        self.m0 = random(sk['N'])
        self.m1 = random(sk['N'])
        print(self.m0)
        print(self.m1)

    def generatePublicKey(self):
        return self.generator, self.public_key

    def getRandomMessages(self):
        self.x0 = random(self.sk['N'])
        self.x1 = random(self.sk['N'])
        return self.x0, self.x1

    def sendMessagesToBob(self, v):
        self.k0 = ((v - self.x0) ** self.sk['d']) % self.sk['N']
        self.k1 = ((v - self.x1) ** self.sk['d']) % self.sk['N']
        self.m0p = self.m0 + self.k0
        self.m1p = self.m1 + self.k1
        return self.m0p, self.m1p


class Bob:
    def __init__(self, pk):
        self.pk = pk
        self.c = 0

    def getV(self, x0, x1):
        # self.b = 0
        self.b = 1
        if self.b == 0:
            self.xb = x0
        else:
            self.xb = x1
        self.k = random(self.pk['N'])
        self.v = (self.xb + self.k ** self.pk['e']) % self.pk['N']
        return self.v

    def mask(self):
        if self.c == 0:
            return self.generator ** self.b
        elif self.c == 1:
            return self.public_key * self.generator ** self.b
        else:
            return None

    def decryptMessages(self, m0p, m1p):
        if self.b == 0:
            return m0p - self.k
        return m1p - self.k


# RSA
rsa = RSA(1024)
sk, pk = rsa.keygen()

alice = Alice(sk)
bob = Bob(pk)
x0, x1 = alice.getRandomMessages()
v = bob.getV(x0, x1)
m0p, m1p = alice.sendMessagesToBob(v)
result = bob.decryptMessages(m0p, m1p)
print(result)