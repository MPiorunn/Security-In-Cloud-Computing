import random, time
from functools import reduce

from charm.core.math.integer import reduce as reduce_int
from charm.toolbox.integergroup import IntegerGroupQ, integer


class Polynomial:
    def __init__(self, coefficient):
        self.coefficient = list(coefficient)

    def getItem(self, item):
        return self.coefficient[item]

    def __set_item__(self, item, value):
        self.coefficient[item] = value

    def __call__(self, element):
        return reduce_int(reduce(lambda acc, a: acc * element + a, reversed(self.coefficient)))


def product(values):
    return reduce(lambda x, y: x * y, values)


def sum(values):
    return reduce(lambda x, y: x + y, values)


def lagrange_interpolation(points, xc):
    return reduce_int(sum([yj * product([(xc - xm) / (xj - xm) for xm, _ in points if xm != xj]) for xj, yj in points]))


class Alice:
    def __init__(self, group, k, degree_of_polynomial):
        self.group = group

        # create Alices polynomial
        self.polynomial = Polynomial([group.random() for _ in range(degree_of_polynomial + 1)])
        # create masked polynomial
        self.masked_polynomial = Polynomial([group.random() for _ in range(degree_of_polynomial * k + 1)])
        # add point 0,0 to polynomial
        self.masked_polynomial.__set_item__(0, integer(0, group.q))

    def Q(self, x, y):
        return reduce_int(self.masked_polynomial(x) + self.polynomial(y))

    def generate_Q(self, R):
        Qs = [(x, self.Q(x, y)) for x, y in R]
        return Qs


class Bob:
    def __init__(self, group, k):
        self.k = k
        self.group = group
        self.alpha = group.random()
        # Generate Bobs polynomial S to mask point A
        self.S = Polynomial([group.random() for _ in range(k + 1)])
        self.S.__set_item__(0, self.alpha)

    def generateR(self, expansion_ratio, degree_of_polynomial):
        self.n = degree_of_polynomial * self.k + 1
        self.N = self.n * expansion_ratio
        self.T = list(range(self.N))
        self.X = [self.group.random() for _ in range(self.N)]

        random.shuffle(self.T)
        self.T = self.T[:self.n]
        R = [(x, self.S(x) if i in self.T else self.group.random()) for i, x in enumerate(self.X)]
        return R

    def getValue(self, Q):
        A = [xq for i, xq in enumerate(Q) if i in self.T]
        value = lagrange_interpolation(A, integer(0, self.group.q))
        return value


group = IntegerGroupQ()
group.paramgen(256)

k = 5  # n = k * degree_of_polynomial
degree_of_polynomial = 10
expansion_ratio = 5

start = time.time()
# generate polynomial and masked polynomial with point (0,0)
alice = Alice(group, k, degree_of_polynomial)
bob = Bob(group, k)

# polynomial used to calculate P(A)
R = bob.generateR(expansion_ratio, degree_of_polynomial)
# generate Q polynomial, one of points of this polynomial will be Bobs wanted
Q = alice.generate_Q(R)

end = time.time()

print(alice)
if alice.polynomial.__call__(bob.alpha) == bob.getValue(Q):
    print("What Alice sent {}".format(alice.polynomial.__call__(bob.alpha)))
    print("What obtained Bob {}".format(bob.getValue(Q)))
    print("Execution time {}s".format(end - start))
