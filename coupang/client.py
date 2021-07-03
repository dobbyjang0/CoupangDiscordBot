import os
import time
import hmac
import hashlib


def _dt():
    os.environ['TZ'] = 'GMT+0'
    return time.strftime('%y%m%d') + 'T'+time.strftime('%H%M%S') + 'Z'


def auth(
        method: str,
        access_key: str,
        secret_key: str,
        path: str,
        query: str = None
):

    dt = _dt()

    if query is not None:
        message = f"{dt}{method}{path}{query}"

    else:
        message = f"{dt}{method}{path}"

    signature = hmac.new(
        bytes(secret_key, "utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    authorization = f"""
    CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={dt}, signature={signature}
    """

    return authorization.strip()


class CoupangClient:

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key


