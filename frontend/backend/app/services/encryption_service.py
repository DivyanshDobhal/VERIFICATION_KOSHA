import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from app.config import settings

class BiometricEncryptionService:
    def __init__(self):
        # 256-bit key (32 bytes)
        raw_key = settings.BIOMETRIC_ENCRYPTION_KEY.encode()[:32]
        if len(raw_key) < 32:
            raw_key = raw_key.ljust(32, b'0')
        self.key = raw_key
        self.aesgcm = AESGCM(self.key)

    def encrypt_embedding(self, embedding_bytes: bytes) -> bytes:
        """Encrypts 128-dimensional embedding vector using AES-256-GCM"""
        nonce = os.urandom(12) # Standard 96-bit nonce
        ciphertext = self.aesgcm.encrypt(nonce, embedding_bytes, None)
        return nonce + ciphertext

    def decrypt_embedding(self, encrypted_payload: bytes) -> bytes:
        """Decrypts AES-256-GCM biometric template payload"""
        nonce = encrypted_payload[:12]
        ciphertext = encrypted_payload[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def generate_template_hash(embedding_bytes: bytes) -> str:
        """Generates cryptographic SHA-256 hash for exact deduplication indexing"""
        return hashlib.sha256(embedding_bytes).hexdigest()

encryption_service = BiometricEncryptionService()
