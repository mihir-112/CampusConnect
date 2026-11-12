"""Password hashing. Owner: publisher-auth.

New passwords use Argon2. Publishers created by the old Flask version have scrypt or PBKDF2
hashes; those still verify, and are upgraded to Argon2 the next time the publisher logs in.
"""
import hashlib
import hmac

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def _verify_legacy(stored: str, password: str) -> bool:
    """Check a Werkzeug-style hash such as 'scrypt:32768:8:1$salt$hex' or 'pbkdf2:sha256:600000$salt$hex'."""
    try:
        method, salt, expected = stored.split("$", 2)
        kind, *params = method.split(":")
        if kind == "scrypt":
            n, r, p = (int(x) for x in params[:3])
            digest = hashlib.scrypt(password.encode(), salt=salt.encode(), n=n, r=r, p=p, maxmem=132 * n * r * p)
        elif kind == "pbkdf2":
            digest = hashlib.pbkdf2_hmac(params[0], password.encode(), salt.encode(), int(params[1] if len(params) > 1 else 600000))
        else:
            return False
    except (ValueError, IndexError):
        return False
    return hmac.compare_digest(digest.hex(), expected)


def is_legacy_hash(stored: str) -> bool:
    return not stored.startswith("$argon2")


def verify_password(stored: str, password: str) -> bool:
    if is_legacy_hash(stored):
        return _verify_legacy(stored, password)
    try:
        return _hasher.verify(stored, password)
    except (VerificationError, InvalidHashError):
        return False
