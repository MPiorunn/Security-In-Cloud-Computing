from charm.toolbox.pairinggroup import PairingGroup, G1, ZR
import time


class Client:

    def __init__(self, group):
        self.group = group

    def Setup(self, z):
        # degree of polynomial
        self.z = z
        # group
        self.g = self.group.random(G1)
        # secret key
        self.sk = self.group.random(ZR)
        # list of block identifiers: ID()
        self.id = []
        for i in range(0, z):
            self.id.append(self.group.random(ZR))

    def Poly(self, group):
        # create a polynomial of degree 'z'
        self.polynomial = []
        #     L_f(x) <- sum(i=0,z) a_i x^i
        for i in range(0, self.z):
            # ai <- SPRNG(sk,id(f),.,i)
            self.polynomial.append(self.group.hash((self.sk, self.id[i], i)))

    def EvaluatePolynomial(self, x):
        if len(self.polynomial) == 0:
            return
        elif len(self.polynomial) == 1:
            result = self.polynomial[0]
            return result
        else:
            y = self.polynomial[0]
            for i in range(len(self.polynomial)):
                y = y + (x ** i) * self.polynomial[i]
            result = y
            return result

    def TagBlock(self, group):
        # f = (m1,...,mz)
        # Tf = ((m1,t1),...,(mz,tz))
        TaggedBlock = []
        # L_f = Poly()
        for i in range(self.z):
            # t_i <- L_f(m_i)
            y = self.EvaluatePolynomial(self.id[i])
            TaggedBlock.append((self.id[i], y))
        return TaggedBlock

    def GenChallenge(self, group):
        # r <- Zq
        r = self.group.random(ZR)
        # x_c <- Zq x_c != m_i
        zero = self.group.random(ZR)
        zero = zero - zero
        xc = self.group.random(ZR)
        for i in range(self.z):
            if xc == self.id[i]:
                xc = group.random(ZR)
                break

        Lf_xc = self.EvaluatePolynomial(xc)
        Lf_xo = self.EvaluatePolynomial(0)

        R = self.g ** r
        # K_f = g^rL_f(x_c)
        self.Kf = R ** Lf_xc
        # H < <g^r, x_c , g^rLf(0))
        H = (R, xc, R ** Lf_xo)
        return H

    def CheckProof(self, pf):
        return self.Kf == pf


class Server:
    def __init__(self, group):
        self.group = group

    def GenProof(self, tagged_block, H):
        # H = <g^r , x_c, g^rLf(0)>
        # poseidon weapon sign - trident - psi

        zero = self.group.random(ZR)
        zero = zero - zero
        psi = []
        # foreach (m_i, t_i) in T_f <- tagged block
        for i in range(len(tagged_block)):
            # psi <- psi U {(m_i,(g^r)^ti)}
            psi.append((tagged_block[i][0], H[0] ** tagged_block[i][1]))
        # trident prim
        # psi prim <- psi U {(0,g^rL_f(0))}
        psi_prim = psi
        psi_prim.insert(0, (zero, H[2]))
        # H[2] = g^rLf(0)

        # Pf <- LIexp (x_c, psi prim)
        Pf = self.LagrangianInterpolation(H[0], H[1], psi_prim)
        return Pf

    def LagrangianInterpolation(self, gr, X, A):
        # A = (<x0,g^(rL0)> , ... , <xz, g^(rLz)>)

        # product of (x-xj)/(xj-xi)
        prod_1 = ()

        # product of g^ [r * L(xi) * prod_1]
        prod_2 = self.group.random(G1)
        prod_2 -= prod_2
        x = []
        y = []
        for i in range(len(A)):
            x.append(A[i][0])
            y.append(A[i][1])
        tmp = self.group.random(ZR)
        for i in range(len(A)):
            tmp = tmp / tmp
            for j in range(len(A)):
                if j != i:
                    tmp = tmp * (X - x[j]) / (x[j] - x[i])
            v = tmp * y[i]
            prod_1 += (v,)
        for i in range(0, len(prod_1)):
            prod_2 += prod_1[i]
        return prod_2


# initialize group, client and server
group = PairingGroup('SS512')
client = Client(group)
server = Server(group)
# start time measurement
start = time.time()
# Procedure 1 - setup algorithm, set polynomial degree
client.Setup(100)

# Procedure 2 - polynomial generating sub-procedure
client.Poly(group)

# Procedure 3 - tag generating procedure
tagged_block = client.TagBlock(group)

# Procedure 4 - Generating a challenge
challenge = client.GenChallenge(group)

# Procedure 5 - Proof procedure GenProof
proof = server.GenProof(tagged_block, challenge)

# Procedure 6 - Proof procedure CheckProof
result = client.CheckProof(proof)

# end time measurement
end = time.time()
if result:
    print("Accept")
    print("Execution time {}s".format(end - start))
else:
    print("Reject")
