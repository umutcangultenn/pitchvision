"""
Access control helpers — org-scoping and role-based guards.

Usage in route handlers:
    from app.services.access_control import assert_org_access, require_role
"""

from __future__ import annotations

from fastapi import HTTPException, status

from app.models import User
from app.models.enums import UserRole

# ── Role hierarchy ─────────────────────────────────────────────────────────────

_ROLE_RANK: dict[UserRole, int] = {
    UserRole.ADMIN: 5,
    UserRole.COACH: 4,
    UserRole.ANALYST: 3,
    UserRole.SCOUT: 2,
    UserRole.VIEWER: 1,
}


def _rank(role: UserRole) -> int:
    return _ROLE_RANK.get(role, 0)


# ── Guards ─────────────────────────────────────────────────────────────────────

def assert_org_access(resource_org_id: int, user: User) -> None:
    """
    Raise HTTP 403 if the resource belongs to a different organization.
    Admins of their own org still pass; no super-admin cross-org access in Phase 2.
    """
    if resource_org_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu kaynağa erişim yetkiniz yok.",
        )


def require_role(user: User, minimum: UserRole) -> None:
    """
    Raise HTTP 403 if the user's role is below the required minimum.

    Example:
        require_role(current_user, UserRole.COACH)
    """
    if _rank(user.role) < _rank(minimum):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Bu işlem için en az '{minimum.value}' rolü gerekli.",
        )


def require_admin(user: User) -> None:
    require_role(user, UserRole.ADMIN)


def require_coach_or_above(user: User) -> None:
    require_role(user, UserRole.COACH)


def require_analyst_or_above(user: User) -> None:
    require_role(user, UserRole.ANALYST)


def require_scout_or_above(user: User) -> None:
    require_role(user, UserRole.SCOUT)
