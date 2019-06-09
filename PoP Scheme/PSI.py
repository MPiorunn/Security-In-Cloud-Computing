#!/usr/bin/python3

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1


class Initiator:
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


class Receiver:
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
    initiator_set = group.random(ZR, set_size - intersecting) + intersection
    receiver_set = group.random(ZR, set_size - intersecting) + intersection
    return initiator_set, receiver_set


def main():
    g = PairingGroup('SS512')
    initiator_set, receiver_set = generate_sets(g, 136, 500)
    initiator = Initiator(g, initiator_set)
    receiver = Receiver(g, receiver_set)

    masked_initiator_set = initiator.get_masked_set()
    masked_receiver_set, challenge = receiver.get_masked_set(masked_initiator_set)
    common_elements = initiator.verify(masked_receiver_set, challenge)
    print("Initiator and receiver have {0} common elements".format(len(common_elements)))


if __name__ == "__main__":
    main()
