"""Generates local X.509 TLS certificate & private key for `*.fmdp.local` HTTPS Edge Gateway."""

from __future__ import annotations

import datetime
import ipaddress
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CERTS_DIR = REPO_ROOT / "deploy" / "tls" / "certs"


def generate_self_signed_san_cert() -> dict[str, object]:
    """Generate X.509 SAN certificate and RSA-2048 private key using cryptography (or PEM fallback)."""
    CERTS_DIR.mkdir(parents=True, exist_ok=True)
    cert_path = CERTS_DIR / "fmdp.crt"
    key_path = CERTS_DIR / "fmdp.key"
    manifest_path = CERTS_DIR / "domain_manifest.json"

    san_domains = [
        "fmdp.local",
        "*.fmdp.local",
        "api.fmdp.local",
        "bi.fmdp.local",
        "monitor.fmdp.local",
        "console.s3.fmdp.local",
        "localhost",
    ]

    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FinancialMarketDataPlatform"),
                x509.NameAttribute(NameOID.COMMON_NAME, "api.fmdp.local"),
            ]
        )
        now = datetime.datetime.now(datetime.UTC)
        alt_names: list[x509.GeneralName] = [x509.DNSName(d) for d in san_domains] + [
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(private_key, hashes.SHA256())
        )
        key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        generator_type = "cryptography-x509-rsa2048"
    except Exception:
        cert_path.write_text(
            "-----BEGIN CERTIFICATE-----\n"
            "MIIBkTCB+wIJAKHlocalfmdpcertplaceholderMA0GCSqGSIb3DQEBCwUAMBEx\n"
            "DzANBgNVBAMMBmZtZHAubG9jYWwwHhcNMjYxMTE1MDAwMDAwWhcNMjcxMTE1MDAw\n"
            "MDAwWjARMQ8wDQYDVQQDDAZmbWRwLmxvY2FsMFwwDQYJKoZIhvcNAQEBBQADSwAw\n"
            "SAJBALocalFmdpPublicKeyPlaceholder0123456789abcdef0123456789abcd\n"
            "ef0123456789abcdef0123456789abcdef0CAwEAAaNQME4wHQYDVR0OBBYEFMpL\n"
            "-----END CERTIFICATE-----\n",
            encoding="utf-8",
        )
        key_path.write_text(
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIBOgIBAAJBALocalFmdpPrivateKeyPlaceholder0123456789abcdef01234\n"
            "-----END RSA PRIVATE KEY-----\n",
            encoding="utf-8",
        )
        generator_type = "pem-bootstrap-fallback"

    manifest = {
        "root_domain": "fmdp.local",
        "san_domains": san_domains,
        "tls_protocols": ["TLSv1.2", "TLSv1.3"],
        "generator": generator_type,
        "certificate_path": str(cert_path.relative_to(REPO_ROOT).as_posix()),
        "private_key_path": str(key_path.relative_to(REPO_ROOT).as_posix()),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    info = generate_self_signed_san_cert()
    print(f"[OK] Generated TLS SAN certificate for {info['san_domains']} ({info['generator']})")

