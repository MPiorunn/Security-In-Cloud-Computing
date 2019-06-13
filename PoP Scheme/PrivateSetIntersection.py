from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
import time


class Alice:
    def __init__(self, group, private_set):
        self.group = group
        self.private_set = private_set
        self.mask = group.random(ZR)

    def get_masked_set(self):
        return [self.group.hash(i, G1) ** self.mask for i in self.private_set]

    def verify(self, receiver_set, challenge):
        common_mask = [i ** self.mask for i in receiver_set]
        common_elements = set(common_mask) & set(challenge)
        return list(common_elements)


class Bob:
    def __init__(self, group, private_set):
        self.group = group
        self.private_set = private_set
        self.mask = group.random(ZR)

    def get_masked_set(self, initiator_set):
        masked_set = [self.group.hash(i, G1) ** self.mask for i in self.private_set]
        challenge = [i ** self.mask for i in initiator_set]
        return masked_set, challenge


def generate_sets(group, intersecting, set_size):
    intersection = group.random(ZR, intersecting)
    alice_set = group.random(ZR, set_size - intersecting) + intersection
    bob_set = group.random(ZR, set_size - intersecting) + intersection
    return alice_set, bob_set


g = PairingGroup('SS512')

intersecting_amount = 100
total_amount = 600
start = time.time()
initiator_set, receiver_set = generate_sets(g, intersecting_amount, total_amount)
alice = Alice(g, initiator_set)
bob = Bob(g, receiver_set)

masked_alice_set = alice.get_masked_set()
masked_bob_set, challenge = bob.get_masked_set(masked_alice_set)
common_elements = alice.verify(masked_bob_set, challenge)
end = time.time()
if intersecting_amount == len(common_elements):
    print("Alice and Bob have {0} common elements".format(len(common_elements)))
    print("Execution time {}s".format(end - start))
else:
    print("Desired amount of intersecting items does not match calculated one")
