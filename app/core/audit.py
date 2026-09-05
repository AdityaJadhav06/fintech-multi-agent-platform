import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditEvent


class AuditLogger:
    """
    Immutable audit logging service for compliance and traceability.
    Computes cryptographic SHA-256 hashes of all payloads.
    """

    @staticmethod
    def compute_hash(payload: Any) -> str:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    async def log_event(
        cls,
        db: AsyncSession,
        org_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        case_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        payload_hash = cls.compute_hash(details or {})
        event = AuditEvent(
            org_id=org_id,
            user_id=user_id,
            case_id=case_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            payload_hash=payload_hash,
            details_json=details or {},
            timestamp=datetime.utcnow(),
        )
        db.add(event)
        return event
