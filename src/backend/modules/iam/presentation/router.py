"""FastAPI Security Defense Middleware & IAM/Auth Router (HTTPS, IP Cipher, JWT Hashing, Rate Limiting)."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import JSONResponse

from src.backend.modules.iam.domain.ports import UserRole
from src.backend.modules.iam.domain.security import (
    CredentialHasher,
    DomainHttpsEndpointPolicy,
    IPAndEndpointCipher,
    JwtSecurityService,
    RateLimitTier,
    SecurityViolationError,
    SlidingWindowRateLimiter,
    inspect_request_for_waf_threats,
)
from src.shared.config import PlatformConfig


def _extract_client_ip(request: Any) -> str:
    forwarded = request.headers.get("x-forwarded-for") or request.headers.get("x-real-ip")
    if forwarded:
        return str(forwarded).split(",")[0].strip()
    if request.client and getattr(request.client, "host", None):
        return str(request.client.host)
    return "127.0.0.1"


def install_security_defense_middleware(
    app: Any,
    config: PlatformConfig | None = None,
    tier_overrides: dict[RateLimitTier, int] | None = None,
) -> tuple[JwtSecurityService, IPAndEndpointCipher, SlidingWindowRateLimiter]:
    """Attach WAF, Trusted Host, IP Encryption/Hashing, Rate Limiting & HTTPS Headers middleware."""
    cfg = config or PlatformConfig()
    domain_policy = DomainHttpsEndpointPolicy(
        root_domain=cfg.platform_domain,
        api_https_origin=f"https://api.{cfg.platform_domain}",
        ws_wss_origin=f"wss://api.{cfg.platform_domain}/ws/v1",
        bi_https_origin=f"https://bi.{cfg.platform_domain}",
        monitor_https_origin=f"https://monitor.{cfg.platform_domain}",
        s3_console_https_origin=f"https://console.s3.{cfg.platform_domain}",
    )
    ip_cipher = IPAndEndpointCipher(cfg.jwt_secret_key)
    jwt_service = JwtSecurityService(
        secret_key=cfg.jwt_secret_key,
        issuer=domain_policy.api_https_origin,
    )
    rate_limiter = SlidingWindowRateLimiter(tier_overrides=tier_overrides)

    @app.middleware("http")
    async def defense_in_depth_middleware(request: Request, call_next: Any) -> Any:
        request_id = f"req_{secrets.token_hex(8)}"
        raw_ip = _extract_client_ip(request)
        client_ip_hash = ip_cipher.hash_ip(raw_ip)
        encrypted_client_ip = ip_cipher.encrypt_address(raw_ip)

        # 1. Host Header Validation (Anti-Host-Header-Injection)
        host_header = (request.headers.get("host") or "localhost").split(":", 1)[0].lower()
        if host_header not in domain_policy.allowed_hosts and not host_header.endswith(f".{domain_policy.root_domain}"):
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "UNTRUSTED_HOST_HEADER",
                        "message": "Request Host header is not authorized by DomainHttpsEndpointPolicy.",
                        "request_id": request_id,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                },
            )

        # 2. WAF Path & Query Threat Inspection (SQLi, Path Traversal, XSS)
        try:
            inspect_request_for_waf_threats(request.url.path, request.url.query)
        except SecurityViolationError as exc:
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "WAF_THREAT_DETECTED",
                        "message": str(exc),
                        "client_ip_token": client_ip_hash,
                        "request_id": request_id,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                },
            )

        # 3. Sliding-Window Rate Limiting per Endpoint Tier & Hashed IP
        tier = rate_limiter.resolve_tier_for_path(request.url.path)
        decision = rate_limiter.check_and_record(client_ip_hash, tier)
        if not decision.allowed:
            return JSONResponse(
                status_code=429,
                headers={
                    "Retry-After": str(decision.reset_after_seconds),
                    "X-RateLimit-Tier": decision.tier.value,
                    "X-RateLimit-Limit": str(decision.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(decision.reset_after_seconds),
                    "X-Client-IP-Token": client_ip_hash,
                    "X-Request-ID": request_id,
                },
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded for tier '{decision.tier.value}' ({decision.limit} req/min).",
                        "details": {
                            "tier": decision.tier.value,
                            "limit_per_minute": decision.limit,
                            "retry_after_seconds": decision.reset_after_seconds,
                            "client_ip_token": client_ip_hash,
                        },
                        "request_id": request_id,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                },
            )

        request.state.client_ip = raw_ip
        request.state.client_ip_hash = client_ip_hash
        request.state.encrypted_client_ip = encrypted_client_ip
        request.state.request_id = request_id

        response = await call_next(request)

        # 4. Inject Hardened HTTPS, Privacy & Rate-Limit Response Headers
        response.headers["Strict-Transport-Security"] = domain_policy.hsts_header
        if request.url.path in ("/api/docs", "/redoc", "/docs"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "connect-src 'self' https: wss:; "
                "frame-ancestors 'none'; base-uri 'self'"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Domain-Origin"] = domain_policy.api_https_origin
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Client-IP-Token"] = client_ip_hash
        response.headers["X-Encrypted-Client-IP"] = encrypted_client_ip
        response.headers["X-RateLimit-Tier"] = decision.tier.value
        response.headers["X-RateLimit-Limit"] = str(decision.limit)
        response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
        response.headers["X-RateLimit-Reset"] = str(decision.reset_after_seconds)
        return response

    return jwt_service, ip_cipher, rate_limiter


def build_iam_security_router(
    jwt_service: JwtSecurityService,
    ip_cipher: IPAndEndpointCipher,
    config: PlatformConfig | None = None,
) -> Any:
    """Build the FastAPI APIRouter for `/api/v1/auth` (JWT, API Keys, Domain/Port Topology)."""
    cfg = config or PlatformConfig()
    domain_policy = DomainHttpsEndpointPolicy(
        root_domain=cfg.platform_domain,
        api_https_origin=f"https://api.{cfg.platform_domain}",
        ws_wss_origin=f"wss://api.{cfg.platform_domain}/ws/v1",
        bi_https_origin=f"https://bi.{cfg.platform_domain}",
        monitor_https_origin=f"https://monitor.{cfg.platform_domain}",
        s3_console_https_origin=f"https://console.s3.{cfg.platform_domain}",
    )
    router = APIRouter()

    @router.post("/token")
    async def issue_jwt_access_token(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))
        role_str = str(payload.get("role", "analyst")).lower()
        if len(username) < 3 or len(password) < 8:
            raise HTTPException(
                status_code=422,
                detail="Username (>=3 chars) and password (>=8 chars) are required.",
            )
        try:
            role_enum = UserRole(role_str)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid role: {role_str}") from exc

        client_ip = getattr(request.state, "client_ip", _extract_client_ip(request))
        password_hash = CredentialHasher.hash_password(password)
        if not CredentialHasher.verify_password(password, password_hash):
            raise HTTPException(status_code=401, detail="Credential verification failed.")

        bundle = jwt_service.issue_token(
            subject=username,
            role=role_enum,
            client_ip=client_ip,
            ttl_seconds=cfg.jwt_access_token_expire_minutes * 60,
        )
        return {
            "data": {
                "access_token": bundle.access_token,
                "token_type": bundle.token_type,
                "expires_in": bundle.expires_in,
                "jti": bundle.jti,
                "token_sha256_hash": bundle.token_sha256_hash,
                "bound_ip_hash": bundle.bound_ip_hash,
                "issuer": bundle.issuer,
            },
            "meta": {
                "security_scheme": "HS256+SHA256_TOKEN_HASH+IP_HMAC_BINDING",
                "password_kdf": "PBKDF2_HMAC_SHA256_210000",
            },
        }

    @router.post("/verify")
    async def verify_jwt_access_token(
        request: Request,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        access_token = str(payload.get("access_token", ""))
        client_ip = getattr(request.state, "client_ip", _extract_client_ip(request))
        try:
            claims = jwt_service.verify_token(access_token, client_ip=client_ip)
        except SecurityViolationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        return {
            "data": {
                "valid": True,
                "subject": claims.sub,
                "role": claims.role.value,
                "capabilities": sorted(claims.capabilities),
                "jti": claims.jti,
                "token_sha256_hash": claims.token_sha256_hash,
                "ip_hash": claims.ip_hash,
                "expires_at": claims.exp,
            }
        }

    @router.post("/revoke")
    async def revoke_jwt_token(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        token_or_hash = str(payload.get("token_or_sha256_hash", ""))
        revoked_hash = jwt_service.revoke_token(token_or_hash)
        return {
            "data": {
                "status": "revoked",
                "revoked_token_sha256_hash": revoked_hash,
            }
        }

    @router.post("/api-keys")
    async def create_scoped_api_key(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        role_str = str(payload.get("role", "service")).lower()
        try:
            role_enum = UserRole(role_str)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid role: {role_str}") from exc

        raw_key, record = CredentialHasher.generate_api_key(role_enum)
        return {
            "data": {
                "api_key_once": raw_key,
                "key_id": record.key_id,
                "key_prefix": record.key_prefix,
                "key_sha256_hash": record.key_sha256_hash,
                "role": record.role.value,
            }
        }

    @router.get("/domains")
    async def get_https_domain_and_encrypted_service_topology() -> dict[str, Any]:
        kafka_host, _, kafka_port_str = cfg.kafka_bootstrap_servers.partition(":")
        kafka_port = int(kafka_port_str or "9092")
        return {
            "data": {
                "root_domain": domain_policy.root_domain,
                "tls_min_version": domain_policy.tls_min_version,
                "public_https_endpoints": {
                    "api_gateway": domain_policy.api_https_origin,
                    "websocket_stream": domain_policy.ws_wss_origin,
                    "bi_superset": domain_policy.bi_https_origin,
                    "observability_grafana": domain_policy.monitor_https_origin,
                    "s3_console_minio": domain_policy.s3_console_https_origin,
                },
                "masked_internal_service_bindings": {
                    "postgres": ip_cipher.mask_service_endpoint("postgres", cfg.postgres_host, cfg.postgres_port),
                    "redis": ip_cipher.mask_service_endpoint("redis", cfg.redis_host, cfg.redis_port),
                    "clickhouse": ip_cipher.mask_service_endpoint(
                        "clickhouse", cfg.clickhouse_host, cfg.clickhouse_http_port
                    ),
                    "kafka": ip_cipher.mask_service_endpoint("kafka", kafka_host, kafka_port),
                },
            }
        }

    return router
