from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
import time


class Alice:
    def __init__(self, group, private_set):
        self.group = group
        self.private_set = private_set
        # generate a mask - random number from group
        self.mask = group.random(ZR)

    def maskSet(self):
        maskedSet = [self.group.hash(i, G1) ** self.mask for i in self.private_set]
        return maskedSet

    def verify(self, receiver_set, challenge):
        common_mask = [i ** self.mask for i in receiver_set]
        # find common elements by & operator
        common_elements = set(common_mask) & set(challenge)
        return list(common_elements)


class Bob:
    def __init__(self, group, private_set):
        self.group = group
        self.private_set = private_set
        self.mask = group.random(ZR)

    def maskSet(self, initiator_set):
        masked_set = [self.group.hash(i, G1) ** self.mask for i in self.private_set]
        challenge = [i ** self.mask for i in initiator_set]
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
