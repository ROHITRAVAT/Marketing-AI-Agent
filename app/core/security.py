def hash_password(password: str) -> str:
    """Hash a plaintext password.

    TODO: Implement with a secure hashing library (e.g., bcrypt) when
    authentication is added.
    """
    raise NotImplementedError("Password hashing not implemented yet")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash.

    TODO: Implement with a secure hashing library (e.g., bcrypt) when
    authentication is added.
    """
    raise NotImplementedError("Password verification not implemented yet")


def create_access_token(data: dict) -> str:
    """Create a signed JWT access token.

    TODO: Implement with a JWT library (e.g., PyJWT) when authentication
    is added.
    """
    raise NotImplementedError("Token creation not implemented yet")