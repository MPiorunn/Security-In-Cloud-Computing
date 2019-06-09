from charm.core.math.integer import isPrime, gcd, random, randomPrime, toInt


class RSA():
    def __init__(self, secparam):
        while True:
            p, q = randomPrime(secparam), randomPrime(secparam)
            if isPrime(p) and isPrime(q) and p != q:
                N = p * q
                phi = (p - 1) * (q - 1)
                break

        while True:
            e = random(phi)
            if not gcd(e, phi) == 1:
                continue
            d = e ** -1
            break

        self.pk = {'N': N, 'e': toInt(e)}
        self.sk = {'phi': phi, 'd': d, 'N': N}

    def keygen(self):
        return self.sk, self.pk


class Alice:
    def __init__(self, sk, pk):
        self.sk = sk
        self.pk = pk
        self.message = [random(sk['N']) for i in range(100)]

    def randomGen(self):
        self.randoms = [random(self.sk['N']) for i in range(100)]
        return self.randoms

    def masquarade(self, vector):
        masqueraded = [((vector - self.randoms[i]) ** self.sk['d']) % self.sk['N'] for i in range(len(self.message))]
        return [self.message[i] + masqueraded[i] for i in range(len(self.message))]


class Bob:
    def __init__(self, pk):
        self.pk = pk

    def computeVector(self, randoms, num):
        self.num = num
        self.k = random(self.pk['N'])
        vector = (randoms[num] + self.k ** self.pk['e']) % self.pk['N']
        return vector

    def computeMessage(self, masqueraded):
        return masqueraded[self.num] - self.k


def main():
    rsa = RSA(1024)
    sk, pk = rsa.keygen()
    alice = Alice(sk, pk)
    bob = Bob(pk)
    randoms = alice.randomGen()
    num = 10
    vector = bob.computeVector(randoms, num)
    masqueraded = alice.masquarade(vector)
    message = bob.computeMessage(masqueraded)
    print(message == alice.message[num])


if __name__ == "__main__":
    main()
