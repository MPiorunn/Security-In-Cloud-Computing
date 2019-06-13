from charm.core.math.integer import isPrime, gcd, random, randomPrime, toInt


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
    def __init__(self, sk, pk):
        self.sk = sk
        self.pk = pk
        self.message = [random(sk['N']) for i in range(100)]

    def randomGen(self):
        self.randoms = [random(self.sk['N']) for i in range(100)]
        return self.randoms

    def mask(self, vector):
        masked = [((vector - self.randoms[i]) ** self.sk['d']) % self.sk['N'] for i in range(len(self.message))]
        return [self.message[i] + masked[i] for i in range(len(self.message))]


class Bob:
    def __init__(self, pk):
        self.pk = pk

    def computeVector(self, randoms, index):
        self.index = index
        self.k = random(self.pk['N'])
        vector = (randoms[index] + self.k ** self.pk['e']) % self.pk['N']
        return vector

    def computeMessage(self, masked):
        return masked[self.index] - self.k


# RSA
rsa = RSA(1024)
sk, pk = rsa.keygen()

# parties init
alice = Alice(sk, pk)
bob = Bob(pk)

randoms = alice.randomGen()
# specify index of message that Bob wants to compute
index = 10

vector = bob.computeVector(randoms, index)

masked = alice.mask(vector)
message = bob.computeMessage(masked)

# scheme verification
if message == alice.message[index]:
    print("SUCCESS")
else:
    print("FAILURE")
