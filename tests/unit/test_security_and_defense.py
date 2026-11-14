"""Comprehensive Security, HTTPS Domain, IP/Port Encryption, JWT Hashing, WAF & Rate-Limit Tests."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from src.backend.main import create_app
from src.backend.modules.iam.domain.ports import UserRole
from src.backend.modules.iam.domain.security import (
    CredentialHasher,
    IPAndEndpointCipher,
    JwtSecurityService,
    RateLimitTier,
    SecurityViolationError,
    SlidingWindowRateLimiter,
    inspect_request_for_waf_threats,
)
from src.shared.config import PlatformConfig


class TestDomainCryptographyAndDefensePrimitives(unittest.TestCase):
    """Tests pure domain security primitives: IP cipher, PBKDF2/SHA-256 hashing, JWT IP binding, Rate Limiter."""

    def setUp(self) -> None:
        self.secret = "fmdp_unit_test_master_secret_key_32_bytes_minimum"
        self.cipher = IPAndEndpointCipher(self.secret)
        self.jwt_service = JwtSecurityService(self.secret, issuer="https://api.fmdp.local")

    def test_ip_hmac_pseudonymization_and_authenticated_encryption(self) -> None:
        h1 = self.cipher.hash_ip("203.0.113.42:51423")
        h2 = self.cipher.hash_ip("203.0.113.42")
        self.assertEqual(h1, h2)
        self.assertTrue(h1.startswith("ip_hm256_"))
        self.assertNotIn("203.0.113.42", h1)

        encrypted = self.cipher.encrypt_address("10.24.0.15:6379")
        self.assertTrue(encrypted.startswith("enc_v1_"))
        self.assertNotIn("6379", encrypted)
        decrypted = self.cipher.decrypt_address(encrypted)
        self.assertEqual(decrypted, "10.24.0.15:6379")

        # Tampering with encrypted token must trigger SecurityViolationError
        tampered = encrypted[:-4] + ("AAAA" if not encrypted.endswith("AAAA") else "BBBB")
        with self.assertRaises(SecurityViolationError):
            self.cipher.decrypt_address(tampered)

    def test_service_endpoint_masking_conceals_raw_host_and_port(self) -> None:
        masked = self.cipher.mask_service_endpoint("clickhouse", "172.18.0.5", 8123)
        self.assertEqual(masked["service_uri"], "svc://clickhouse.fmdp.internal")
        self.assertTrue(masked["binding_id"].startswith("bind_"))
        self.assertNotIn("172.18.0.5", str(masked))
        self.assertNotIn("8123", str(masked))
        self.assertEqual(
            self.cipher.decrypt_address(masked["encrypted_endpoint"]),
            "172.18.0.5:8123",
        )

    def test_password_pbkdf2_and_api_key_sha256_hashing(self) -> None:
        pw_hash = CredentialHasher.hash_password("StrongPass!2026")
        self.assertTrue(pw_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(CredentialHasher.verify_password("StrongPass!2026", pw_hash))
        self.assertFalse(CredentialHasher.verify_password("WrongPass!2026", pw_hash))

        raw_key, record = CredentialHasher.generate_api_key(UserRole.OPERATOR)
        self.assertTrue(raw_key.startswith("fmdp_live_"))
        self.assertEqual(len(record.key_sha256_hash), 64)
        self.assertTrue(CredentialHasher.verify_api_key(raw_key, record))
        self.assertFalse(CredentialHasher.verify_api_key(raw_key + "x", record))

    def test_jwt_signing_ip_binding_and_sha256_revocation(self) -> None:
        bundle = self.jwt_service.issue_token(
            subject="sec_analyst_01",
            role=UserRole.ANALYST,
            client_ip="198.51.100.25",
            ttl_seconds=900,
            now_epoch=1_700_000_000,
        )
        self.assertEqual(len(bundle.token_sha256_hash), 64)

        # Valid verification from original client IP
        claims = self.jwt_service.verify_token(
            bundle.access_token,
            client_ip="198.51.100.25",
            now_epoch=1_700_000_100,
        )
        self.assertEqual(claims.sub, "sec_analyst_01")
        self.assertEqual(claims.role, UserRole.ANALYST)
        self.assertIn("agent:trigger", claims.capabilities)

        # Token replay from a different IP must be rejected
        with self.assertRaises(SecurityViolationError):
            self.jwt_service.verify_token(
                bundle.access_token,
                client_ip="203.0.113.99",
                now_epoch=1_700_000_100,
            )

        # Expired token must be rejected
        with self.assertRaises(SecurityViolationError):
            self.jwt_service.verify_token(
                bundle.access_token,
                client_ip="198.51.100.25",
                now_epoch=1_700_001_000,
            )

        # Revoked token hash must be rejected
        self.jwt_service.revoke_token(bundle.token_sha256_hash)
        with self.assertRaises(SecurityViolationError):
            self.jwt_service.verify_token(
                bundle.access_token,
                client_ip="198.51.100.25",
                now_epoch=1_700_000_100,
            )

    def test_sliding_window_rate_limiter_enforces_quotas(self) -> None:
        limiter = SlidingWindowRateLimiter(
            window_seconds=60,
            tier_overrides={RateLimitTier.AGENT_TRIGGER: 2},
        )
        ip_hash = "ip_hm256_testclient01"
        d1 = limiter.check_and_record(ip_hash, RateLimitTier.AGENT_TRIGGER, now_monotonic=100.0)
        d2 = limiter.check_and_record(ip_hash, RateLimitTier.AGENT_TRIGGER, now_monotonic=110.0)
        d3 = limiter.check_and_record(ip_hash, RateLimitTier.AGENT_TRIGGER, now_monotonic=120.0)
        self.assertTrue(d1.allowed)
        self.assertTrue(d2.allowed)
        self.assertFalse(d3.allowed)
        self.assertEqual(d3.remaining, 0)
        self.assertGreater(d3.reset_after_seconds, 0)

    def test_waf_blocks_sqli_xss_and_path_traversal(self) -> None:
        with self.assertRaises(SecurityViolationError):
            inspect_request_for_waf_threats("/api/v1/market/prices/BTCUSDT", "q=1 UNION SELECT * FROM users")
        with self.assertRaises(SecurityViolationError):
            inspect_request_for_waf_threats("/api/v1/../../etc/passwd", "")
        with self.assertRaises(SecurityViolationError):
            inspect_request_for_waf_threats("/api/v1/market", "x=<script>alert(1)</script>")


class TestFastApiDefenseInDepthGatewayAndAuthEndpoints(unittest.TestCase):
    """Tests HTTPS headers, masked service ports, JWT/API-key endpoints, WAF 403, and Rate Limit 429."""

    def setUp(self) -> None:
        self.config = PlatformConfig(
            platform_domain="fmdp.local",
            jwt_secret_key="fmdp_integration_test_secret_key_32_bytes_long",
        )
        self.app = create_app(
            config=self.config,
            tier_overrides={RateLimitTier.AUTH: 4, RateLimitTier.MARKET_READ: 20},
        )
        self.client = TestClient(self.app)

    def test_https_security_headers_and_masked_readiness_endpoints(self) -> None:
        resp = self.client.get(
            "/api/v1/health/ready",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "203.0.113.77"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("max-age=63072000", resp.headers["Strict-Transport-Security"])
        self.assertEqual(resp.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(resp.headers["X-Frame-Options"], "DENY")
        self.assertEqual(resp.headers["X-Domain-Origin"], "https://api.fmdp.local")
        self.assertTrue(resp.headers["X-Client-IP-Token"].startswith("ip_hm256_"))
        self.assertTrue(resp.headers["X-Encrypted-Client-IP"].startswith("enc_v1_"))

        body = resp.json()
        deps = body["dependencies"]
        self.assertEqual(deps["redis"]["service_uri"], "svc://redis.fmdp.internal")
        self.assertEqual(deps["clickhouse"]["service_uri"], "svc://clickhouse.fmdp.internal")
        self.assertEqual(deps["postgres"]["service_uri"], "svc://postgres.fmdp.internal")
        self.assertNotIn("6379", str(deps))
        self.assertNotIn("8123", str(deps))
        self.assertNotIn("5432", str(deps))

        # Verify Swagger UI (/api/docs) and OpenAPI schema (/api/openapi.json) over api.fmdp.local
        docs_resp = self.client.get("/api/docs", headers={"Host": "api.fmdp.local"})
        openapi_resp = self.client.get("/api/openapi.json", headers={"Host": "api.fmdp.local"})
        self.assertEqual(docs_resp.status_code, 200)
        self.assertIn("Swagger UI", docs_resp.text)
        self.assertIn("cdn.jsdelivr.net", docs_resp.headers["Content-Security-Policy"])
        self.assertEqual(openapi_resp.status_code, 200)
        self.assertIn("/api/v1/auth/token", openapi_resp.json()["paths"])

    def test_auth_token_issue_verify_ip_replay_block_and_revoke(self) -> None:
        issue_resp = self.client.post(
            "/api/v1/auth/token",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "198.51.100.12"},
            json={
                "username": "quant_operator",
                "password": "SecurePassword#2026",
                "role": "operator",
            },
        )
        self.assertEqual(issue_resp.status_code, 200)
        token_data = issue_resp.json()["data"]
        access_token = token_data["access_token"]
        token_hash = token_data["token_sha256_hash"]
        self.assertEqual(token_data["issuer"], "https://api.fmdp.local")

        # Verify from same IP succeeds
        verify_ok = self.client.post(
            "/api/v1/auth/verify",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "198.51.100.12"},
            json={"access_token": access_token},
        )
        self.assertEqual(verify_ok.status_code, 200)
        self.assertEqual(verify_ok.json()["data"]["role"], "operator")

        # Replay from spoofed/different IP fails with 401
        verify_diff_ip = self.client.post(
            "/api/v1/auth/verify",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "203.0.113.200"},
            json={"access_token": access_token},
        )
        self.assertEqual(verify_diff_ip.status_code, 401)

        # Revoke by SHA-256 hash and verify rejection
        revoke_resp = self.client.post(
            "/api/v1/auth/revoke",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "198.51.100.12"},
            json={"token_or_sha256_hash": token_hash},
        )
        self.assertEqual(revoke_resp.status_code, 200)

        verify_after_revoke = self.client.post(
            "/api/v1/auth/verify",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "198.51.100.12"},
            json={"access_token": access_token},
        )
        self.assertEqual(verify_after_revoke.status_code, 401)

    def test_untrusted_host_waf_403_and_rate_limit_429(self) -> None:
        # 1. Untrusted Host Header -> 400
        bad_host = self.client.get("/api/v1/health/live", headers={"Host": "phishing.attacker.org"})
        self.assertEqual(bad_host.status_code, 400)
        self.assertEqual(bad_host.json()["error"]["code"], "UNTRUSTED_HOST_HEADER")

        # 2. WAF SQL injection attempt -> 403
        waf_resp = self.client.get(
            "/api/v1/market/prices/BTCUSDT?provider=binance%20UNION%20SELECT%20password_hash%20FROM%20users",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "192.0.2.55"},
        )
        self.assertEqual(waf_resp.status_code, 403)
        self.assertEqual(waf_resp.json()["error"]["code"], "WAF_THREAT_DETECTED")

        # 3. Rate limit on /api/v1/auth/domains (AUTH tier limit=4) -> 5th request returns 429
        for _ in range(4):
            r = self.client.get(
                "/api/v1/auth/domains",
                headers={"Host": "api.fmdp.local", "X-Forwarded-For": "192.0.2.88"},
            )
            self.assertEqual(r.status_code, 200)
        r_limited = self.client.get(
            "/api/v1/auth/domains",
            headers={"Host": "api.fmdp.local", "X-Forwarded-For": "192.0.2.88"},
        )
        self.assertEqual(r_limited.status_code, 429)
        self.assertEqual(r_limited.json()["error"]["code"], "RATE_LIMIT_EXCEEDED")
        self.assertIn("Retry-After", r_limited.headers)


if __name__ == "__main__":
    unittest.main()
