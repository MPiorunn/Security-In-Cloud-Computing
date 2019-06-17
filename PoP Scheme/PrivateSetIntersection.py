from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
import time


class Alice:
    def __init__(self, group, private_set):
        self.group = group
        # X = {x1,...,Xn}
        self.private_set = private_set
        # generate a secret key a(alfa)
        self.secretKey = group.random(ZR)

    def maskSet(self):
        # A[i] = (H(xi))^a
        maskedSet = [self.group.hash(item, G1) ** self.secretKey for item in self.private_set]
        return maskedSet

    def verify(self, receiver_set, challenge):
        # D[i] = B[i]**a
        common_mask = [item ** self.secretKey for item in receiver_set]
        # find common elements by '&' operator in sets C , D
        common_elements = set(common_mask) & set(challenge)
        return list(common_elements)


class Bob:
    def __init__(self, group, private_set):
        self.group = group
        # Y = {y1,...,yM}
        self.private_set = private_set
        # generate secret key B
        self.secretKey = group.random(ZR)

    def maskSet(self, initiator_set):
        # B[i] = (H(yi))**b
        masked_set = [self.group.hash(item, G1) ** self.secretKey for item in self.private_set]
        # C[i] = A[i]**b
        challenge = [item ** self.secretKey for item in initiator_set]
        return masked_set, challenge


def generate_sets(group, intersecting, alice_size, bob_size):
    # generate intersection set
    intersection = group.random(ZR, intersecting)
    # generate Alice set of size (alice_size - intersection) and add intersecting items
    alice_set = group.random(ZR, alice_size - intersecting) + intersection
    # generate Bob set of size (bob_size - intersection) and add intersecting items
    bob_set = group.random(ZR, bob_size - intersecting) + intersection
    return alice_set, bob_set


g = PairingGroup('SS512')

# protocol parameters
# amount of the same items
intersecting_amount = 100
# amount of items in Alice set
Alice_amount = 300
# amount of items in Bob set
Bob_amount = 400

print("Alice has {} elements".format(Alice_amount))
print("Bob has {} elements".format(Bob_amount))
start = time.time()

# generate Alice and Bob set
aliceSet, bobSet = generate_sets(g, intersecting_amount, Alice_amount, Bob_amount)

alice = Alice(g, aliceSet)
bob = Bob(g, bobSet)

maskedAliceSet = alice.maskSet()

maskedBobSet, challenge = bob.maskSet(maskedAliceSet)

common_elements = alice.verify(maskedBobSet, challenge)

end = time.time()
if intersecting_amount == len(common_elements):
    print("Alice and Bob have {0} common elements".format(len(common_elements)))
    print("Execution time {}s".format(end - start))
else:
    print("Desired amount of intersecting items does not match calculated one")


'''
     Alice(X,N,a)                         Bob(Y,M,b)

A[i] = H(xi)^a
                          A
                         ->                 
                                           B[i] = H(yi)^b
                                           C[i] = A[i]^b = H(xi)^ab
                        B,C
                        <-

D[i] = B[i]**a = H(yi)^ab

teraz Alice ma oba sety i moze znalezc wspolne elementy




'''