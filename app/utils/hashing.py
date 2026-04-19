"""
Password Hashing Utilities.

This module provides secure password hashing and verification using the
Argon2 algorithm via Passlib's CryptContext.

Argon2 is a modern, memory‑hard hashing algorithm designed to resist:
- GPU cracking
- Brute‑force attacks
- Side‑channel attacks

This module is used throughout the authentication system to ensure
passwords are never stored or compared in plain text.
"""

from passlib.context import CryptContext
from passlib.exc import UnknownHashError


# =========================================================
# ARGON2 HASHING CONFIGURATION
# =========================================================
# Configure Passlib to use Argon2 with strong security parameters.
# These settings increase resistance to brute‑force attacks.
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",

    # Argon2 parameters (strong defaults)
    argon2__memory_cost=102400,   # 100 MB memory usage
    argon2__parallelism=8,        # Number of threads
    argon2__time_cost=3           # Number of hashing iterations
)


class PasswordHasher:
    """
    Provides secure password hashing and verification using Argon2.

    This class exposes two static methods:
        - hash_password(): Hashes a plain password
        - verify_password(): Verifies a password against a stored hash

    The class is stateless and safe to use across the application.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain user password using Argon2.

        Args:
            password (str): The raw password provided by the user.

        Returns:
            str: A secure Argon2 hash suitable for database storage.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a stored Argon2 hash.

        Args:
            plain_password (str): The raw password provided by the user.
            hashed_password (str): The stored Argon2 hash from the database.

        Returns:
            bool: True if the password matches, False otherwise.

        Notes:
            - Returns False if the hash is invalid or corrupted.
            - UnknownHashError is caught to prevent crashes.
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except UnknownHashError:
            # Hash is invalid or from an unsupported scheme
            return False