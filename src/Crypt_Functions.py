from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.asymmetric import padding as padding2
from cryptography.hazmat.primitives.asymmetric import dh

import random

# BLOCK_SIZE = 16
# key = os.urandom(BLOCK_SIZE)
# iv = os.urandom(BLOCK_SIZE)
# ctr = os.urandom(BLOCK_SIZE)


def aes_ctr(msg, key, ctr):

    cipher = Cipher(algorithms.AES(key), modes.CTR(ctr),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(msg) + encryptor.finalize()

    return cipher_text


def aes_ctr_decrypt(cipher_text, key, ctr):
    cipher = Cipher(algorithms.AES(key), modes.CTR(ctr),
                    backend=default_backend())
    decryptor = cipher.decryptor()
    msg = decryptor.update(cipher_text) + decryptor.finalize()

    return msg


def hmac_sha256(msg, key):

    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(msg)
    return h.finalize()


def rsa_enc_der(msg, pk_path):
    with open(pk_path, "rb") as key_file:
        public_key = serialization.load_der_public_key(
        key_file.read(),
        backend=default_backend() )

    ciphertext = public_key.encrypt(
     msg,
     padding2.OAEP(
         mgf=padding2.MGF1(algorithm=hashes.SHA1()),
         algorithm=hashes.SHA1(),
         label=None
     )
    )
    return ciphertext


def rsa_dec_der(ciphertext, sk_path):

    with open(sk_path, "rb") as key_file:
        private_key = serialization.load_der_private_key(
        key_file.read(),
        password=None,
        backend=default_backend())

    msg = private_key.decrypt(
    ciphertext,
    padding2.OAEP(
     mgf=padding2.MGF1(algorithm=hashes.SHA1()),
     algorithm=hashes.SHA1(),
     label=None
     )
    )
    return msg


class Diffie_Hellman:

    # generate prime with generate_prime
    def __init__(self, p, g):

        # 2048bit primes
        # generator = 2
        self.pn = dh.DHParameterNumbers(p, g)
        self.parameters = self.pn.parameters(default_backend())
        # dh.generate_parameters(
        #     generator=2, key_size=2048, backend=default_backend())
        self.private = self.parameters.generate_private_key()
        self.public = self.private.public_key()

    def get_private_key(self):
        """ Return the private key (a) """
        return self.private

    def get_public_key(self):
        return self.public

    # amirali
    def check_other_public_key(self, other_contribution):
        # check if the other public key is valid based on NIST SP800-56
        # 2 <= g^b <= p-2 and Lagrange for safe primes (g^bq)=1, q=(p-1)/2

        if 2 <= other_contribution and other_contribution <= self.p - 2:
            if pow(other_contribution, (self.p - 1) // 2, self.p) == 1:
                return True
        return False

    def df_key_exchange(self, peer_public_key):
        shared_key = self.private.exchange(peer_public_key)

        return shared_key

    # create diffie-hellman values
    # encrypt it with public key of B
    # return encrypted {g^a}_pk-receiver


def hash_sha256(inp):

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(inp)
    return digest.finalize()


# generate prime number using isPrime
def generate_prime(n=1024):

    p = pow(2, n - 1) + 1
    while not isPrime(p):
        # n += 2
        p = random.randint(pow(2, n - 1), pow(2, n) - 1)
    return p


def decompose(p):

    dec = p - 1
    r = 0

    while not dec & 1:

        r += 1
        dec /= 2

    u = (p - 1) / pow(2, r)

    return r, u


def isPrime(p):

    t = 40  # strength

    if p == 1:
        return False
    if not p & 1:  # even
        return False

    # if perfect power
    # if isPerfectPower(p):
    #     return False
    r, u = decompose(p)

    for i in xrange(t):

        a = random.randint(1, p - 1)

        k = pow(a, u, p)

        if k != 1 and k != p - 1:

            for j in xrange(1, r + 1):
                n = pow(2, j) * u

                k = pow(a, n, p)

                if k != p - 1:
                    return False
    return True


def cryptrand(Num, n=1024):
    return random.SystemRandom().getrandbits(n) % Num


# SRP implementation
class SRP_server():

    def __init__(self, N):

        self.g = 2
        self.N = N

        N_g = self.N + self.g
        self.k = hash_sha256(N_g)

    def srp_server_pass_verf(self, username, password):

        # password verifier generation
        salt = cryptrand(64)

        # x, private
        pass_code = salt + username + ':' + password
        x = hash_sha256(pass_code)

        # pass verifier
        v = pow(self.g, x, self.N)

        # DB ENTRY   <username,password verifier(v), salt, salt_creation_date>
        return username, v, salt

    def srp_server_accept_login(self, username, client_A):

    # 2
    # TODO
    # get salt and pass verifier for username from db
        v = 'verification'
        salt = 'salt'  # self.get_salt_username(username)

        b = cryptrand()
        B = (self.k * v + pow(self.g, b, self.N)) % self.N

    # 3
        u = hash_sha256(client_A + B)

    # 5
        session_key = hash_sha256(pow(client_A * pow(v, u, self.N), b, self.N))

        return session_key

    # TODO
    # verify proof of session key


class SRP_client():

    def __init__(self, username, password, client, g, N):

        self.client = client

        self.g = g
        self.N = N
        self.A = ''

        self.username = username
        self.password = password

        self.session_key = 'key'

    def srp_client_login_msg(self):

        # get username(I), password

        # self.username = raw_input('Enter Username: ')
        # self.password = getpass.getpass('Enter password: ')

    # 1
        msg = ''
        try:
            a = cryptrand(N=self.N)
            self.A = pow(self.g, a, self.N)

            msg = {'username': self.username, 'A': self.A, 'N': self.N}

        except Exception as e:

            print e
            exit(1)

        return msg

    def srp_create_session_key(self, B, salt):

        server_B = B

    # 3 Random scrambling parameter

        u = hash_sha256(self.A + server_B)

    # 4

        pass_code = salt + self.username + ':' + self.password
        x = hash_sha256(pass_code)


        self.session_key = hash_sha256(pow(server_B - self.k * pow(self.g, x, self.N), a + u * x, self.N))

    # TODO
    # send proof of session key



