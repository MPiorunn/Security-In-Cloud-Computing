from charm.toolbox.pairinggroup import PairingGroup, G1, ZR


class Client:

    def __init__(self, group):
        self.group = group

    def Setup(self, z):
        self.z = z
        self.g = self.group.random(G1)
        self.sk = self.group.random(ZR)
        self.file_id = []
        for i in range(0, z):
            self.file_id.append(self.group.random(ZR))

    def Poly(self, group):
        # create a polynomial of degree 'z'
        self.polynomial = []
        for i in range(0, self.z):
            # ai <- SPRNG(sk,id(f),.,i)
            self.polynomial.append(self.group.hash((self.sk, self.file_id[i], i)))

    #     L_f(x) <- sum a_i x^i

    def EvaluatePolynomial(self, coefficients, x):
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
        for i in range(self.z):
            y = self.EvaluatePolynomial(self.polynomial, self.file_id[i])
            TaggedBlock.append((self.file_id[i], y))
        return TaggedBlock

    def GenChallenge(self, group):
        # r <- Zq
        r = self.group.random(ZR)
        # x_c <- Zq x_c != m_i
        xc = self.group.random(ZR)
        for i in range(self.z):
            if xc == self.file_id[i]:
                xc = group.random(ZR)
                break

        Lf_xc = self.EvaluatePolynomial(self.polynomial, xc)
        Lf_xo = self.EvaluatePolynomial(self.polynomial, 0)

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
        # poseidon weapon sign - trident
        psi = []
        for i in range(len(tagged_block)):
            # psi <- psi U {(m_i,(g^r)^ti)}
            psi.append((tagged_block[i][0], H[0] ** tagged_block[i][1]))
        # trident prim
        # psi prim <- psi U {(0,g^rL_f(0))}
        psi_prim = psi
        psi_prim.insert(0, (0, H[2]))
        # Pf <- LIexp (x_c, psi prim)
        Pf = self.LagrangianInterpolation(H[1], psi_prim)
        return Pf

    def LagrangianInterpolation(self, S, points):
        # CREATE A POLYNOMIAL L_f (x) FROM POINTS (x_1,y_1)...(x_n, y_n)
        r = ()
        t = self.group.random(ZR)
        t = t / t
        for i in range(len(points)):
            for j in range(len(points)):
                if j != i:
                    t = t * (S - points[j][0]) / (points[i][0] - points[j][0])
            v = t * points[i][1]
            r += (v,)
            t /= t
        p = self.group.random(G1)
        p -= p
        for i in range(0, len(r)):
            p += r[i]
        return p


# initialize group, client and server
group = PairingGroup('SS512')
client = Client(group)
server = Server(group)

# Procedure 1 - setup algorithm
client.Setup(10)

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

if result:
    print("Accept")
else:
    print("Reject")
