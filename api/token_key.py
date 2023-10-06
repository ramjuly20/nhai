import secrets

def generate_token_key(length = 32):
    return secrets.token_hex(length)
