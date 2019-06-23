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
        self.count = count
        self.sk = sk
        self.pk = pk
        self.message = [random(sk['N']) for i in range(self.count)]

    def generateA(self):
        self.A = [random(self.sk['N']) for i in range(self.count)]
        return self.A

    def mask(self, vector):
        masked = [((vector - self.A[i]) ** self.sk['d']) % self.sk['N'] for i in range(len(self.message))]
        return [self.message[i] + masked[i] for i in range(len(self.message))]


class Bob:
    def __init__(self, pk):
        self.pk = pk

    def getV(self, A, index):
        self.index = index
        self.k = random(self.pk['N'])
        v = (A[index] + self.k ** self.pk['e']) % self.pk['N']
        return v

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
A = alice.generateA()

# specify index of message that Bob wants to compute
index = 10

v = bob.getV(A, index)

masked = alice.mask(v)
message = bob.computeMessage(masked)

end = time.time()
# scheme verification
if message == alice.message[index]:
    print("SUCCESS")
    print("Execution time {}s".format(end - start))

else:
    print("FAILURE")



'''
Alice (sk,pk,count)                                       Bob (pk)

A = random


'''
