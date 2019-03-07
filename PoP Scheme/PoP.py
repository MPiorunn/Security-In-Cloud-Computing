'''

Proof of Posession for Cloud Storage via Lagrangian Interpolation Techinques

'''
import random as r
from charm.toolbox.integergroup import IntegerGroupQ


class Client:

    def mama(self):
        return 'x'


class Server:

    def tata(self):
        return 'y'


def generate(params):
    g = IntegerGroupQ(1024)
    g.paramgen(params)
    skc = g.random()
    return g, skc


def SPRNG(skc, id, i):
    return group.hash(i, skc, id)  # warning hash is not working?


def generateF(limit):
    f = []
    for i in range(0, limit):
        f.append(r.random())
    return f


def generatePolynomial(skc, z, id):
    Lf = {}
    for i in range(0, z):
        ai = SPRNG(skc, id, i)
        xi = i
        Lf[xi] = ai
    return Lf


def polynomial(L, b):
    result = 0
    for i in range(0, len(L)):
        result = result + (L[i] * (b ** i))
    return result


def generateTags(block, skc, id):
    L = generatePolynomial(skc, 10, id)
    T = []

    for i in range(0, len(block)):
        T.append({block[i]: polynomial(L, block[i])})

    return T


(group, SKc) = generate(1024)
f = generateF(10)
IDf = group.random()
T = generateTags(f, SKc, IDf)
for t in T:
    print(t)
