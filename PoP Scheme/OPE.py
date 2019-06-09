import random
from functools import reduce

from charm.core.math.integer import reduce as reduce_int
from charm.toolbox.integergroup import IntegerGroupQ, integer


class Polynomial:
    def __init__(self, coef):
        self.coef = list(coef)

    def __get_item__(self, item):
        return self.coef[item]

    def __set_item__(self, item, value):
        self.coef[item] = value

    def __call__(self, element):
        return reduce_int(reduce(lambda acc, a: acc * element + a, reversed(self.coef)))


def product(values):
    return reduce(lambda x, y: x * y, values)


def sum(values):
    return reduce(lambda x, y: x + y, values)


def lagrange_interpolation(points, xc):
    return reduce_int(sum([yj * product([(xc - xm) / (xj - xm) for xm, _ in points if xm != xj]) for xj, yj in points]))


class Alice:
    def __init__(self, group, k, degree_of_polynomial):
        self.group = group
        self.polynomial = Polynomial([group.random() for _ in range(degree_of_polynomial + 1)])
        self.masked_polynomial = Polynomial([group.random() for _ in range(degree_of_polynomial * k + 1)])
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
        self.S = Polynomial([group.random() for _ in range(k + 1)])
        self.S.__set_item__(0, self.alpha)

    def generate_R(self, expansion_ratio, degree_of_polynomial):
        self.n = degree_of_polynomial * self.k + 1
        self.N = self.n * expansion_ratio
        self.T = list(range(self.N))
        self.X = [self.group.random() for _ in range(self.N)]

        random.shuffle(self.T)
        self.T = self.T[:self.n]
        R = [(x, self.S(x) if i in self.T else self.group.random()) for i, x in enumerate(self.X)]
        return R

    def get_value(self, Q):
        A = [xq for i, xq in enumerate(Q) if i in self.T]
        value = lagrange_interpolation(A, integer(0, self.group.q))
        return value


def main():
    group = IntegerGroupQ()
    group.paramgen(256)

    k = 5  # n = k * degree_of_polynomial
    degree_of_polynomial = 10
    expansion_ratio = 5

    alice = Alice(group, k, degree_of_polynomial)
    bob = Bob(group, k)

    R = bob.generate_R(expansion_ratio, degree_of_polynomial)
    Q = alice.generate_Q(R)

    print(alice.polynomial.__call__(bob.alpha) == bob.get_value(Q))


if __name__ == "__main__":
    main()
