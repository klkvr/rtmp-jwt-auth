import os

JWT_KEY = os.environ.get("JWT_KEY")
TOKEN_EXPIRATION_DELTA = int(os.environ.get("TOKEN_EXPIRATION_DELTA"))
REDIS_URL = os.environ.get("REDIS_URL")
