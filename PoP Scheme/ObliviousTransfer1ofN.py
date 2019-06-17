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
    def __init__(self, sk, pk, count):
        self.sk = sk
        self.pk = pk
        self.message = [random(sk['N']) for i in range(count)]

    def randomGen(self):
        self.randoms = [random(self.sk['N']) for i in range(count)]
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

# parties init ,
messages_count = 100
alice = Alice(sk, pk, messages_count)
bob = Bob(pk)

start = time.time()
randoms = alice.randomGen()
# specify index of message that Bob wants to compute
index = 10

vector = bob.computeVector(randoms, index)

masked = alice.mask(vector)
message = bob.computeMessage(masked)

end = time.time()
# scheme verification
if message == alice.message[index]:
    print("SUCCESS")
    print("Execution time {}s".format(end - start))

else:
    print("FAILURE")
