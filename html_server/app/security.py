import bcrypt

# Password hashing primitives only. Session tokens are handled by
# Starlette's SessionMiddleware (signed cookie via itsdangerous), wired up
# in app/main.py -- no separate token code needed here.


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
