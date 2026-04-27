"""
Password Hashing Utilities.

This module provides secure password hashing and verification using the
Argon2 algorithm via Passlib's CryptContext.

Argon2 is a modern, memory-hard hashing algorithm designed to resist:
- GPU cracking
- Brute-force attacks
- Side-channel attacks

This module is used throughout the authentication system to ensure
passwords are never stored or compared in plain text.
"""

import os
from passlib.context import CryptContext
from passlib.exc import UnknownHashError


# =========================================================
# ARGON2 HASHING CONFIGURATION (UVICORN SAFE DEFAULTS)
# =========================================================


# IMPORTANT:
# Each password hash/verify temporarily consumes this much memory.
# Adjust values via environment variables if your server has more RAM.
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",

    # Argon2 parameters (Uvicorn-friendly defaults)
    argon2__memory_cost=int(os.getenv("ARGON2_MEMORY_COST", 65536)),  # 64 MB
    argon2__parallelism=int(os.getenv("ARGON2_PARALLELISM", 4)),      # Threads
    argon2__time_cost=int(os.getenv("ARGON2_TIME_COST", 3))           # Iterations
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

        Raises:
            ValueError: If the password is empty.
            TypeError: If the password is not a string.
        """
        if not isinstance(password, str):
            raise TypeError("Password must be a string")

        if not password:
            raise ValueError("Password must not be empty")

        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a stored Argon2 hash.

        Returns False for:
        - Invalid hashes
        - Corrupted hashes
        - Unsupported schemes
        - Bad input types
        """
        if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
            return False

        if not plain_password or not hashed_password:
            return False

        try:
            return pwd_context.verify(plain_password, hashed_password)
        except UnknownHashError:
            # Covers UnknownHashError, invalid/corrupt hashes, etc.
            return False