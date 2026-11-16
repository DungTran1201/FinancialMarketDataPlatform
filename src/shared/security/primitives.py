"""Shared Cryptographic Masking, Sliding-Window Rate Limiting, HTTPS Policy & WAF Guardrails."""

from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import re
import secrets
import time
import urllib.parse
from dataclasses import dataclass
from enum import StrEnum

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
        "backend-api",
        "svc-api-gateway",
        "svc-data-plane-v01",
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
    """Derive a 256-bit (32-byte) cryptographic key via HMAC-SHA256 domain separation."""
    return hmac.new(
        master_secret.encode("utf-8"),
        f"fmdp-key-derivation:{purpose}".encode(),
        hashlib.sha256,
    ).digest()


class IPAndEndpointCipher:
    """Encrypts and hashes IP addresses and internal service host:port bindings.

    1. Deterministic HMAC-SHA256 pseudonymization (`ip_hm256_*`) for rate limiting & logs.
    2. Standard NIST AES-256-GCM (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`)
       authenticated encryption (`enc_v1_*`) for reversible security audit inspection
       without ever exposing raw IPs or container ports in API responses.
    """

    _AAD = b"fmdp:endpoint-and-ip-aead:v1"

    def __init__(self, secret_key: str) -> None:
        if not secret_key or len(secret_key.strip()) < 16:
            raise ValueError("Security secret_key must be at least 16 characters.")
        self._hmac_key = _derive_subkey(secret_key, "ip-pseudonym-hmac")
        self._enc_key = _derive_subkey(secret_key, "endpoint-cipher-aes256gcm")
        self._aesgcm = AESGCM(self._enc_key)

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
        """Encrypt an IP address or internal host:port endpoint using standard AES-256-GCM (AEAD)."""
        nonce = secrets.token_bytes(12)  # 96-bit standard NIST GCM nonce
        plaintext_bytes = plaintext_ip_or_endpoint.encode("utf-8")
        ciphertext_with_tag = self._aesgcm.encrypt(nonce, plaintext_bytes, self._AAD)
        return f"enc_v1_{_b64url_encode(nonce + ciphertext_with_tag)}"

    def decrypt_address(self, token: str) -> str:
        """Verify GCM authentication tag and decrypt an `enc_v1_*` address token."""
        if not token.startswith("enc_v1_"):
            raise SecurityViolationError("Invalid encrypted address token prefix.")
        try:
            raw = _b64url_decode(token[len("enc_v1_") :])
        except Exception as exc:
            raise SecurityViolationError("Malformed base64 encrypted address token.") from exc
        if len(raw) < 29:  # 12-byte nonce + 16-byte GCM tag + >=1 byte payload
            raise SecurityViolationError("Encrypted address token is truncated.")
        nonce = raw[:12]
        ciphertext_with_tag = raw[12:]
        try:
            plaintext_bytes = self._aesgcm.decrypt(nonce, ciphertext_with_tag, self._AAD)
        except InvalidTag as exc:
            raise SecurityViolationError("Encrypted address token AES-GCM tag verification failed.") from exc
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
