from fastapi import HTTPException, status
from app.core.auth import AuthenticatedUser


def verify_tenant_access(user: AuthenticatedUser, target_org_id: str) -> None:
    """
    Enforces strict multi-tenant data isolation.
    """
    if user.org_id != target_org_id and user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Tenant isolation violation.",
        )
