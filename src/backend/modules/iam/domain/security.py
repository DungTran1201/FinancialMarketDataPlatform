"""Pure Domain Security Primitives: HTTPS Domain Policy, IP/Port Encryption, JWT Hashing & Rate Limiting.

Adheres strictly to Clean Architecture: zero external framework or I/O driver imports.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import re
import secrets
import time
import urllib.parse
from dataclasses import dataclass
from enum import StrEnum

from src.backend.modules.iam.domain.ports import ROLE_CAPABILITIES, UserRole
from src.shared.domain.primitives import DomainError


class SecurityViolationError(DomainError):
    """Raised when an authentication, token integrity, IP binding, or WAF rule is violated."""


class RateLimitExceededError(DomainError):
    """Raised when a client exceeds the sliding-window rate limit for an endpoint tier."""


class RateLimitTier(StrEnum):
    """Endpoint rate-limit tiers defined in docs/specifications/api-specification.md."""

    MARKET_READ = "market_read"  # 120 requests / minute
    HEAVY_ANALYTICS = "heavy_analytics"  # 30 requests / minute
    AUTH = "auth"  # 10 requests / minute
    AGENT_TRIGGER = "agent_trigger"  # 5 requests / minute


TIER_LIMITS_PER_MINUTE: dict[RateLimitTier, int] = {
    RateLimitTier.MARKET_READ: 120,
    RateLimitTier.HEAVY_ANALYTICS: 30,
    RateLimitTier.AUTH: 10,
    RateLimitTier.AGENT_TRIGGER: 5,
}


@dataclass(frozen=True, slots=True)
class DomainHttpsEndpointPolicy:
    """Canonical HTTPS domain & subdomain routing policy hiding internal container IPs/ports."""

    root_domain: str = "fmdp.local"
    api_https_origin: str = "https://api.fmdp.local"
    ws_wss_origin: str = "wss://api.fmdp.local/ws/v1"
    bi_https_origin: str = "https://bi.fmdp.local"
    monitor_https_origin: str = "https://monitor.fmdp.local"
    s3_console_https_origin: str = "https://console.s3.fmdp.local"
    tls_min_version: str = "TLSv1.3"
    hsts_header: str = "max-age=63072000; includeSubDomains; preload"
    allowed_hosts: tuple[str, ...] = (
        "fmdp.local",
        "api.fmdp.local",
        "bi.fmdp.local",
        "monitor.fmdp.local",
        "console.s3.fmdp.local",
        "localhost",
        "127.0.0.1",
        "testserver",
    )


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(encoded: str) -> bytes:
    padding = "=" * ((4 - len(encoded) % 4) % 4)
    return base64.urlsafe_b64decode((encoded + padding).encode("ascii"))


def _derive_subkey(master_secret: str, purpose: str) -> bytes:
    return hmac.new(
        master_secret.encode("utf-8"),
        f"fmdp-key-derivation:{purpose}".encode(),
        hashlib.sha256,
    ).digest()


def _keystream_xor(data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Generate a deterministic SHA-256 counter-mode keystream and XOR with data."""
    out = bytearray(len(data))
    block_count = (len(data) + 31) // 32
    for counter in range(block_count):
        counter_bytes = counter.to_bytes(8, "big")
        block = hmac.new(key, nonce + counter_bytes, hashlib.sha256).digest()
        start = counter * 32
        end = min(start + 32, len(data))
        for idx in range(start, end):
            out[idx] = data[idx] ^ block[idx - start]
    return bytes(out)


class IPAndEndpointCipher:
    """Encrypts and hashes IP addresses and internal service host:port bindings.

    1. Deterministic HMAC-SHA256 pseudonymization (`ip_hm256_*`) for rate limiting & logs.
    2. Authenticated Encrypt-then-MAC (`enc_v1_*`) for reversible security audit inspection
       without ever exposing raw IPs or container ports in API responses.
    """

    def __init__(self, secret_key: str) -> None:
        if not secret_key or len(secret_key.strip()) < 16:
            raise ValueError("Security secret_key must be at least 16 characters.")
        self._hmac_key = _derive_subkey(secret_key, "ip-pseudonym-hmac")
        self._enc_key = _derive_subkey(secret_key, "endpoint-cipher-enc")
        self._mac_key = _derive_subkey(secret_key, "endpoint-cipher-mac")

    @staticmethod
    def normalize_ip(raw_ip: str) -> str:
        candidate = (raw_ip or "127.0.0.1").split(",")[0].strip()
        if candidate.startswith("[") and "]" in candidate:
            candidate = candidate[1 : candidate.index("]")]
        elif candidate.count(":") == 1 and "." in candidate:
            candidate = candidate.split(":", 1)[0]
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            return "0.0.0.0"

    def hash_ip(self, raw_ip: str) -> str:
        """Return privacy-preserving HMAC-SHA256 token for a client IP address."""
        normalized = self.normalize_ip(raw_ip)
        digest = hmac.new(
            self._hmac_key,
            normalized.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:24]
        return f"ip_hm256_{digest}"

    def encrypt_address(self, plaintext_ip_or_endpoint: str) -> str:
        """Encrypt an IP address or internal host:port endpoint using Encrypt-then-MAC."""
        nonce = secrets.token_bytes(16)
        plaintext_bytes = plaintext_ip_or_endpoint.encode("utf-8")
        ciphertext = _keystream_xor(plaintext_bytes, self._enc_key, nonce)
        tag = hmac.new(self._mac_key, nonce + ciphertext, hashlib.sha256).digest()[:16]
        return f"enc_v1_{_b64url_encode(nonce + tag + ciphertext)}"

    def decrypt_address(self, token: str) -> str:
        """Verify MAC in constant time and decrypt an `enc_v1_*` address token."""
        if not token.startswith("enc_v1_"):
            raise SecurityViolationError("Invalid encrypted address token prefix.")
        try:
            raw = _b64url_decode(token[len("enc_v1_") :])
        except Exception as exc:
            raise SecurityViolationError("Malformed base64 encrypted address token.") from exc
        if len(raw) < 33:
            raise SecurityViolationError("Encrypted address token is truncated.")
        nonce = raw[:16]
        tag = raw[16:32]
        ciphertext = raw[32:]
        expected_tag = hmac.new(self._mac_key, nonce + ciphertext, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(tag, expected_tag):
            raise SecurityViolationError("Encrypted address token MAC verification failed.")
        plaintext_bytes = _keystream_xor(ciphertext, self._enc_key, nonce)
        return plaintext_bytes.decode("utf-8")

    def mask_service_endpoint(self, service_alias: str, host: str, port: int) -> dict[str, str]:
        """Mask an internal service host:port into an encrypted token & HTTPS/logical URI."""
        raw_endpoint = f"{host}:{port}"
        endpoint_fingerprint = hmac.new(
            self._hmac_key,
            f"{service_alias}:{raw_endpoint}".encode(),
            hashlib.sha256,
        ).hexdigest()[:16]
        return {
            "service_uri": f"svc://{service_alias}.fmdp.internal",
            "binding_id": f"bind_{endpoint_fingerprint}",
            "encrypted_endpoint": self.encrypt_address(raw_endpoint),
            "transport_security": "INTERNAL_ISOLATED_NET",
        }


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


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    """Outcome of a sliding-window rate limit check."""

    allowed: bool
    tier: RateLimitTier
    limit: int
    remaining: int
    reset_after_seconds: int
    client_ip_hash: str


class SlidingWindowRateLimiter:
    """In-memory / Redis-compatible sliding-window rate limiter keyed by hashed IP or principal."""

    def __init__(
        self,
        window_seconds: int = 60,
        tier_overrides: dict[RateLimitTier, int] | None = None,
    ) -> None:
        self._window_seconds = window_seconds
        self._limits = dict(TIER_LIMITS_PER_MINUTE)
        if tier_overrides:
            self._limits.update(tier_overrides)
        self._buckets: dict[str, list[float]] = {}

    @staticmethod
    def resolve_tier_for_path(path: str) -> RateLimitTier:
        normalized = path.lower()
        if normalized.startswith("/api/v1/auth"):
            return RateLimitTier.AUTH
        if normalized.startswith("/api/v1/agents/runs"):
            return RateLimitTier.AGENT_TRIGGER
        if normalized.startswith("/api/v1/analytics"):
            return RateLimitTier.HEAVY_ANALYTICS
        return RateLimitTier.MARKET_READ

    def check_and_record(
        self,
        client_ip_hash: str,
        tier: RateLimitTier,
        now_monotonic: float | None = None,
    ) -> RateLimitDecision:
        now = time.monotonic() if now_monotonic is None else now_monotonic
        cutoff = now - self._window_seconds
        bucket_key = f"{tier.value}:{client_ip_hash}"
        timestamps = [ts for ts in self._buckets.get(bucket_key, []) if ts > cutoff]

        max_requests = self._limits[tier]
        if len(timestamps) >= max_requests:
            oldest = timestamps[0]
            reset_after = max(1, int(round((oldest + self._window_seconds) - now)))
            self._buckets[bucket_key] = timestamps
            return RateLimitDecision(
                allowed=False,
                tier=tier,
                limit=max_requests,
                remaining=0,
                reset_after_seconds=reset_after,
                client_ip_hash=client_ip_hash,
            )

        timestamps.append(now)
        self._buckets[bucket_key] = timestamps
        remaining = max(0, max_requests - len(timestamps))
        reset_after = int(self._window_seconds)
        return RateLimitDecision(
            allowed=True,
            tier=tier,
            limit=max_requests,
            remaining=remaining,
            reset_after_seconds=reset_after,
            client_ip_hash=client_ip_hash,
        )


_WAF_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(\.\./|\.\.\\)", re.IGNORECASE),
    re.compile(r"(union\s+select|drop\s+table|insert\s+into|delete\s+from)", re.IGNORECASE),
    re.compile(r"(<script\b|javascript:)", re.IGNORECASE),
    re.compile(r"(;\s*shutdown\b|;\s*exec\b)", re.IGNORECASE),
)


def inspect_request_for_waf_threats(path: str, query_string: str) -> None:
    """Inspect URI path and query parameters (including URL-decoded forms) for SQLi, XSS & Path Traversal."""
    raw_combined = f"{path}?{query_string}"
    decoded_once = urllib.parse.unquote_plus(raw_combined)
    decoded_twice = urllib.parse.unquote_plus(decoded_once)
    for candidate in (raw_combined, decoded_once, decoded_twice):
        for pattern in _WAF_FORBIDDEN_PATTERNS:
            if pattern.search(candidate):
                raise SecurityViolationError("WAF blocked suspicious request pattern in URI or query parameters.")
