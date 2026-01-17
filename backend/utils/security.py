import base64
import hashlib
import hmac
import json
import time
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def create_token(secret: str, subject: str, ttl_seconds: int) -> str:
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + ttl_seconds}
    payload_bytes = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=")
    sig = hmac.new(secret.encode("utf-8"), payload_b64, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=")
    return payload_b64.decode("utf-8") + "." + sig_b64.decode("utf-8")


def _b64_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def verify_token(secret: str, token: str) -> dict[str, Any] | None:
    try:
        payload_part, sig_part = token.split(".", 1)
    except ValueError:
        return None

    expected_sig = hmac.new(secret.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256).digest()
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b"=").decode("utf-8")
    if not hmac.compare_digest(expected_sig_b64, sig_part):
        return None

    try:
        payload = json.loads(_b64_decode(payload_part).decode("utf-8"))
    except Exception:
        return None

    now = int(time.time())
    if int(payload.get("exp", 0)) < now:
        return None

    return payload

