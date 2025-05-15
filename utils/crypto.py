import base64
import hashlib
import binascii
import os
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import json

class Crypto:
    # Các khóa cố định từ ứng dụng gốc
    keys = [
        "oppo1997", "baed2017", "java7865", "231uiedn", "09e32ji6",
        "0oiu3jdy", "0pej387l", "2dkliuyt", "20odiuye", "87j3id7w"
    ]
    
    @staticmethod
    def get_key(key):
        index = int(key[0])
        combined_key = Crypto.keys[index] + key[4:12]
        return combined_key.encode('utf-8')
    
    @staticmethod
    def get_random_key():
        return os.urandom(32)  # 256-bit key
    
    @staticmethod
    def get_iv():
        return os.urandom(16)  # 16 bytes for AES
    
    @staticmethod
    def enc_dec_aes_ctr(data, key, iv, mode):
        if mode == "encrypt":
            cipher = AES.new(key, AES.MODE_CTR, initial_value=iv, nonce=b'')
            return cipher.encrypt(data)
        else:  # decrypt
            cipher = AES.new(key, AES.MODE_CTR, initial_value=iv, nonce=b'')
            return cipher.decrypt(data)
    
    @staticmethod
    def enc_aes_ctr(data, key, iv):
        return Crypto.enc_dec_aes_ctr(data, key, iv, "encrypt")
    
    @staticmethod
    def dec_aes_ctr(data, key, iv):
        return Crypto.enc_dec_aes_ctr(data, key, iv, "decrypt")
    
    @staticmethod
    def enc_dec_aes_ecb(data, key, mode):
        if mode == "encrypt":
            cipher = AES.new(key, AES.MODE_ECB)
            # Ensure data is padded to a multiple of 16 bytes for AES
            padded_data = data + (16 - len(data) % 16) * chr(16 - len(data) % 16).encode('utf-8')
            return cipher.encrypt(padded_data)
        else:  # decrypt
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(data)
            # Remove padding
            padding_len = decrypted[-1]
            return decrypted[:-padding_len]
    
    @staticmethod
    def enc_aes_ecb(data, key):
        return Crypto.enc_dec_aes_ecb(data, key, "encrypt")
    
    @staticmethod
    def dec_aes_ecb(data, key):
        return Crypto.enc_dec_aes_ecb(data, key, "decrypt")
    
    @staticmethod
    def encrypt_ctr(buf):
        # Generate a pseudo key: first character is a random digit, followed by 14 random characters
        import random
        key_pseudo = str(random.randint(0, 9)) + ''.join(random.choice('0123456789') for _ in range(14))
        
        # Get the real key
        key_real = Crypto.get_key(key_pseudo)
        
        # Generate the IV using MD5 of the real key
        md = hashlib.md5()
        md.update(key_real)
        iv = md.digest()
        
        # Encrypt using AES-CTR
        encrypted = Crypto.enc_aes_ctr(buf.encode('utf-8'), key_real, iv)
        
        # Return the base64 encoded ciphertext concatenated with the key pseudo
        return base64.b64encode(encrypted).decode('utf-8') + key_pseudo
    
    @staticmethod
    def decrypt_ctr(buf):
        # Decode the base64-encoded ciphertext (excluding the last 15 characters for the key pseudo)
        data = base64.b64decode(buf[:-15])
        
        # Get the real key using the key pseudo
        key_real = Crypto.get_key(buf[-15:])
        
        # Generate the IV using MD5 of the real key
        md = hashlib.md5()
        md.update(key_real)
        iv = md.digest()
        
        # Decrypt using AES-CTR
        decrypted = Crypto.dec_aes_ctr(data, key_real, iv)
        
        # Convert decrypted bytes to String
        return decrypted.decode('utf-8')
    
    @staticmethod
    def encrypt_ctr_v2(data):
        key = Crypto.get_random_key()
        iv = Crypto.get_iv()
        encrypted = Crypto.enc_aes_ctr(data.encode('utf-8'), key, iv)
        return (
            base64.b64encode(encrypted).decode('utf-8'),
            base64.b64encode(key).decode('utf-8'),
            base64.b64encode(iv).decode('utf-8')
        )
    
    @staticmethod
    def decrypt_ctr_v2(data, key, iv):
        decoded_data = base64.b64decode(data)
        decoded_key = base64.b64decode(key)
        decoded_iv = base64.b64decode(iv)
        decrypted = Crypto.dec_aes_ctr(decoded_data, decoded_key, decoded_iv)
        return decrypted.decode('utf-8')
    
    @staticmethod
    def encrypt_ecb(data):
        import random
        key_pseudo = str(random.randint(0, 9)) + ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(14))
        key_real = Crypto.get_key(key_pseudo)
        encrypted = Crypto.enc_aes_ecb(data.encode('utf-8'), key_real)
        return base64.b64encode(encrypted).decode('utf-8') + key_pseudo
    
    @staticmethod
    def decrypt_ecb(data):
        encrypted_data = base64.b64decode(data[:-15])
        key = Crypto.get_key(data[-15:])
        plain = Crypto.dec_aes_ecb(encrypted_data, key)
        return plain.decode('utf-8')
    
    @staticmethod
    def sha256(data):
        digest = hashlib.sha256()
        digest.update(data.encode('utf-8'))
        hash_bytes = digest.digest()
        return ''.join(f'{b:02X}' for b in hash_bytes)
    
    @staticmethod
    def encrypt_rsa(data, pub_key):
        # Convert base64 encoded public key to RSA key
        pubkey_data = base64.b64decode(pub_key)
        rsa_key = RSA.import_key(pubkey_data)
        
        # Create cipher
        cipher = PKCS1_OAEP.new(rsa_key)
        
        # Encrypt data
        encrypted = cipher.encrypt(data)
        return encrypted
    
    @staticmethod
    def generate_protected_key(key, pub_key):
        encrypted = Crypto.encrypt_rsa(key.encode('utf-8'), pub_key.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')