# app/config/sec.py
import secrets

def generate_token_keys():
    """Generate secure ACCESS and REFRESH token secret keys."""
    access_key = secrets.token_hex(64)
    refresh_key = secrets.token_hex(64)
    return access_key, refresh_key


if __name__ == "__main__":
    access, refresh = generate_token_keys()
    print("ACCESS_TOKEN_SECRET_KEY =", access)
    print("REFRESH_TOKEN_SECRET_KEY =", refresh)
