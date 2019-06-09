from charm.toolbox.pairinggroup import PairingGroup, G1, ZR


class Client():
    group = 0
    z = 0  # number of subblocks
    sk = 0
    g = 0
    file_id = []
    polynomial = []
    Kf = 0

    def __init__(self, group):
        Client.group = group

    def Setup(self, z):
        Client.z = z
        Client.g = Client.group.random(G1)
        Client.sk = Client.group.random(ZR)

        for i in range(0, 10):
            Client.file_id.append(Client.group.random(ZR))

    def Poly(self, group):
        for i in range(0, Client.z):
            Client.polynomial.append(Client.group.hash((Client.sk, Client.file_id[i], i)))

    def EvaluatePolynomial(coefficients, x):
        if len(coefficients) == 0:
            return
        elif len(coefficients) == 1:
            result = coefficients[0]
            return result
        else:
            y = coefficients[len(coefficients) - 1]
            for i in range(len(coefficients) - 2, 0, -1):
                y = y * x
                y = y + coefficients[i]
            result = y
            return result

    def TagBlock(self, group):
        TaggedBlock = []
        for i in range(Client.z):
            y = Client.EvaluatePolynomial(Client.polynomial, Client.file_id[i])
            TaggedBlock.append((Client.file_id[i], y))
        return TaggedBlock

    def GenChallenge(self, group):
        zero = Client.group.random(ZR)
        zero -= zero
        r = Client.group.random(ZR)
        xc = Client.group.random(ZR)
        for i in range(Client.z):
            if (xc == Client.file_id[i]):
                xc = group.random(ZR)
                i = 0
        Lfxc = Client.EvaluatePolynomial(Client.polynomial, xc)
        Lfxo = Client.EvaluatePolynomial(Client.polynomial, zero)
        R = Client.g ** r
        Client.Kf = R ** Lfxc
        H = (R, xc, R ** Lfxo)
        return H

    def CheckProof(self, Pf):
        if Client.Kf == Pf:
            return True
        else:
            return False


class Server():
    group = 0

    def __init__(self, group):
        Server.group = group

    def GenProof(self, TaggedBlock, H):
        zero = Server.group.random(ZR)
        zero = zero - zero
        psi = []
        for i in range(len(TaggedBlock)):
            psi.append((TaggedBlock[i][0], H[0] ** TaggedBlock[i][1]))
        psi_prim = psi
        psi_prim.insert(0, (zero, H[2]))
        Pf = Server.LagrangeInterpolation(H[1], psi_prim)
        return Pf

    def LagrangeInterpolation(S, points):
        r = ()
        t = Server.group.random(ZR)
        t = t / t
        for i in range(len(points)):
            for j in range(len(points)):
                if j != i:
                    t = t * (S - points[j][0]) / (points[i][0] - points[j][0])
            v = t * points[i][1]
            r += (v,)
            t = t / t
        p = Server.group.random(G1)
        p = p - p
        for i in range(0, len(r)):
            p += r[i]
        return p


def main():
    group = PairingGroup('SS512')

    c = Client(group)
    c.Setup(10)
    c.Poly(group)
    tagged_block = c.TagBlock(group)
    challenge = c.GenChallenge(group)

    s = Server(group)
    proof = s.GenProof(tagged_block, challenge)

    result = c.CheckProof(proof)

    if result:
        print("SUCCESS")
    else:
        print("ERROR")


main()
