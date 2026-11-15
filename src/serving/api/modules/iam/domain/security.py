"""IAM Bounded-Context Credential Hashing & IP-HMAC Bound JWT Security Service (`COMP-006`)."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass

from src.serving.api.modules.iam.domain.ports import ROLE_CAPABILITIES, UserRole
from src.shared.security.primitives import (
    IPAndEndpointCipher,
    SecurityViolationError,
    _b64url_decode,
    _b64url_encode,
    _derive_subkey,
)


@dataclass(frozen=True, slots=True)
class HashedApiKeyRecord:
    """Stored representation of a scoped API key (raw secret is never persisted)."""

    key_id: str
    key_prefix: str
    key_sha256_hash: str
    role: UserRole
    created_at_epoch: int


class CredentialHasher:
    """PBKDF2-HMAC-SHA256 password hashing and SHA-256 API key hashing."""

    PBKDF2_ITERATIONS = 210_000

    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        if len(plain_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            cls.PBKDF2_ITERATIONS,
        )
        return f"pbkdf2_sha256${cls.PBKDF2_ITERATIONS}${_b64url_encode(salt)}${_b64url_encode(derived)}"

    @classmethod
    def verify_password(cls, plain_password: str, stored_hash: str) -> bool:
        try:
            scheme, iter_str, salt_b64, hash_b64 = stored_hash.split("$", 3)
            if scheme != "pbkdf2_sha256":
                return False
            iterations = int(iter_str)
            salt = _b64url_decode(salt_b64)
            expected = _b64url_decode(hash_b64)
        except Exception:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(candidate, expected)

    @staticmethod
    def hash_raw_token_sha256(raw_token: str) -> str:
        """Compute deterministic SHA-256 hex digest of a JWT or API key."""
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def generate_api_key(cls, role: UserRole) -> tuple[str, HashedApiKeyRecord]:
        """Generate a scoped API key (`fmdp_live_...`) and its SHA-256 hashed record."""
        key_id = f"ak_{secrets.token_hex(6)}"
        secret_part = secrets.token_urlsafe(24)
        raw_api_key = f"fmdp_live_{key_id}_{secret_part}"
        record = HashedApiKeyRecord(
            key_id=key_id,
            key_prefix=raw_api_key[:18],
            key_sha256_hash=cls.hash_raw_token_sha256(raw_api_key),
            role=role,
            created_at_epoch=int(time.time()),
        )
        return raw_api_key, record

    @classmethod
    def verify_api_key(cls, raw_api_key: str, record: HashedApiKeyRecord) -> bool:
        candidate_hash = cls.hash_raw_token_sha256(raw_api_key)
        return hmac.compare_digest(candidate_hash, record.key_sha256_hash)


@dataclass(frozen=True, slots=True)
class IssuedJwtBundle:
    """Returned when issuing a signed, IP-bound JWT access token."""

    access_token: str
    token_type: str
    expires_in: int
    jti: str
    token_sha256_hash: str
    bound_ip_hash: str
    issuer: str


@dataclass(frozen=True, slots=True)
class JwtClaims:
    """Validated claims extracted from an HS256 JWT token."""

    sub: str
    role: UserRole
    capabilities: frozenset[str]
    iss: str
    aud: str
    iat: int
    exp: int
    jti: str
    ip_hash: str
    token_sha256_hash: str


class JwtSecurityService:
    """RFC 7519 HS256 JWT issuer & verifier with SHA-256 token hashing and IP-hash binding."""

    def __init__(
        self,
        secret_key: str,
        issuer: str = "https://api.fmdp.local",
        audience: str = "fmdp-platform",
    ) -> None:
        if not secret_key or len(secret_key.strip()) < 16:
            raise ValueError("JWT secret_key must be at least 16 characters.")
        self._signing_key = _derive_subkey(secret_key, "jwt-hs256-signing")
        self._ip_cipher = IPAndEndpointCipher(secret_key)
        self._issuer = issuer
        self._audience = audience
        self._revoked_token_hashes: set[str] = set()

    def issue_token(
        self,
        subject: str,
        role: UserRole,
        client_ip: str = "127.0.0.1",
        ttl_seconds: int = 900,
        now_epoch: int | None = None,
    ) -> IssuedJwtBundle:
        now = int(time.time()) if now_epoch is None else int(now_epoch)
        jti = f"jti_{secrets.token_hex(12)}"
        ip_hash = self._ip_cipher.hash_ip(client_ip)
        capabilities = sorted(ROLE_CAPABILITIES.get(role, frozenset()))

        header = {"alg": "HS256", "typ": "JWT", "kid": "fmdp-hs256-v1"}
        payload = {
            "sub": subject,
            "role": role.value,
            "capabilities": capabilities,
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "exp": now + ttl_seconds,
            "jti": jti,
            "ip_hash": ip_hash,
        }
        signing_input = (
            f"{_b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))}."
            f"{_b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))}"
        )
        signature = hmac.new(
            self._signing_key,
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        compact_token = f"{signing_input}.{_b64url_encode(signature)}"
        token_sha256 = CredentialHasher.hash_raw_token_sha256(compact_token)
        return IssuedJwtBundle(
            access_token=compact_token,
            token_type="Bearer",
            expires_in=ttl_seconds,
            jti=jti,
            token_sha256_hash=token_sha256,
            bound_ip_hash=ip_hash,
            issuer=self._issuer,
        )

    def revoke_token(self, token_or_sha256_hash: str) -> str:
        """Revoke a JWT either by raw compact string or by its 64-char SHA-256 hex digest."""
        if len(token_or_sha256_hash) == 64 and all(c in "0123456789abcdef" for c in token_or_sha256_hash.lower()):
            token_hash = token_or_sha256_hash.lower()
        else:
            token_hash = CredentialHasher.hash_raw_token_sha256(token_or_sha256_hash)
        self._revoked_token_hashes.add(token_hash)
        return token_hash

    def verify_token(
        self,
        compact_token: str,
        client_ip: str | None = None,
        now_epoch: int | None = None,
    ) -> JwtClaims:
        parts = compact_token.split(".")
        if len(parts) != 3:
            raise SecurityViolationError("Malformed JWT structure.")
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(
            self._signing_key,
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        try:
            provided_sig = _b64url_decode(signature_b64)
            header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
            payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        except Exception as exc:
            raise SecurityViolationError("Invalid JWT encoding.") from exc

        if header.get("alg") != "HS256":
            raise SecurityViolationError("Unsupported JWT signing algorithm.")
        if not hmac.compare_digest(provided_sig, expected_sig):
            raise SecurityViolationError("JWT signature verification failed.")

        token_hash = CredentialHasher.hash_raw_token_sha256(compact_token)
        if token_hash in self._revoked_token_hashes:
            raise SecurityViolationError("JWT token has been revoked.")

        now = int(time.time()) if now_epoch is None else int(now_epoch)
        exp = int(payload.get("exp", 0))
        if now >= exp:
            raise SecurityViolationError("JWT token has expired.")

        if payload.get("iss") != self._issuer or payload.get("aud") != self._audience:
            raise SecurityViolationError("JWT issuer or audience mismatch.")

        bound_ip_hash = str(payload.get("ip_hash", ""))
        if client_ip is not None:
            caller_ip_hash = self._ip_cipher.hash_ip(client_ip)
            if not hmac.compare_digest(bound_ip_hash, caller_ip_hash):
                raise SecurityViolationError("JWT client IP binding mismatch (potential token replay detected).")

        role = UserRole(str(payload["role"]))
        caps = frozenset(payload.get("capabilities", ())) | ROLE_CAPABILITIES.get(role, frozenset())
        return JwtClaims(
            sub=str(payload["sub"]),
            role=role,
            capabilities=caps,
            iss=str(payload["iss"]),
            aud=str(payload["aud"]),
            iat=int(payload["iat"]),
            exp=exp,
            jti=str(payload["jti"]),
            ip_hash=bound_ip_hash,
            token_sha256_hash=token_hash,
        )
