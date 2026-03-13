"""
Ed25519 identity helpers for agent registration handshake (skeleton).

Provides key generation, signing, and verification utilities with fallbacks if libs are not installed.
Store public key fingerprints in data/iam_agents.db (or Redis) as part of the onboarding flow.
"""

import os

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
except Exception:
    SigningKey = None


def generate_keypair_hex() -> tuple:
    """Return (private_hex, public_hex)"""
    if SigningKey:
        sk = SigningKey.generate()
        vk = sk.verify_key
        return sk.encode(encoder=HexEncoder).decode(), vk.encode(encoder=HexEncoder).decode()
    # Fallback using cryptography
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        sk = ed25519.Ed25519PrivateKey.generate()
        pk = sk.public_key()
        sk_raw = sk.private_bytes(encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw, encryption_algorithm=serialization.NoEncryption())
        pk_raw = pk.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        import binascii
        return binascii.hexlify(sk_raw).decode(), binascii.hexlify(pk_raw).decode()
    except Exception:
        raise RuntimeError("No suitable crypto backend available; install pynacl or cryptography")


def sign_message_hex(private_hex: str, message: str) -> str:
    if SigningKey:
        sk = SigningKey(private_hex, encoder=HexEncoder)
        signed = sk.sign(message.encode())
        return signed.signature.hex()
    # Fallback
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import binascii
    sk_raw = binascii.unhexlify(private_hex)
    sk = Ed25519PrivateKey.from_private_bytes(sk_raw)
    signature = sk.sign(message.encode())
    return binascii.hexlify(signature).decode()


def verify_signature_hex(public_hex: str, message: str, signature_hex: str) -> bool:
    if SigningKey:
        vk = VerifyKey(public_hex, encoder=HexEncoder)
        try:
            vk.verify(message.encode(), bytes.fromhex(signature_hex))
            return True
        except Exception:
            return False
    # Fallback
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    import binascii
    pk_raw = binascii.unhexlify(public_hex)
    signature = binascii.unhexlify(signature_hex)
    pk = Ed25519PublicKey.from_public_bytes(pk_raw)
    try:
        pk.verify(signature, message.encode())
        return True
    except Exception:
        return False
