"""IAM domain entities & RBAC roles (Pure Domain Layer)."""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    """Platform RBAC roles ordered by least privilege."""

    VIEWER = "viewer"
    ANALYST = "analyst"
    OPERATOR = "operator"
    ADMIN = "admin"
    SERVICE = "service"


ROLE_CAPABILITIES: dict[UserRole, frozenset[str]] = {
    UserRole.VIEWER: frozenset({"market:read", "historical:read", "analytics:read", "reports:read"}),
    UserRole.ANALYST: frozenset(
        {"market:read", "historical:read", "analytics:read", "reports:read", "agent:trigger"}
    ),
    UserRole.OPERATOR: frozenset(
        {
            "market:read",
            "historical:read",
            "analytics:read",
            "reports:read",
            "agent:trigger",
            "backfill:trigger",
            "catalog:write",
        }
    ),
    UserRole.ADMIN: frozenset(
        {
            "market:read",
            "historical:read",
            "analytics:read",
            "reports:read",
            "agent:trigger",
            "backfill:trigger",
            "catalog:write",
            "iam:admin",
        }
    ),
}

