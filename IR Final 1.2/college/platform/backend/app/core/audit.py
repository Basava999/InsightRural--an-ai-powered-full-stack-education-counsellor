"""Audit logging for API requests."""

import hashlib
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("audit")


def log_request(
    action: str,
    endpoint: str,
    user_id: Optional[str] = None,
    ip: Optional[str] = None,
    status_code: int = 200,
    payload: Optional[Any] = None,
) -> None:
    payload_hash = None
    if payload:
        payload_hash = hashlib.sha256(str(payload).encode()).hexdigest()[:16]

    logger.info(
        "AUDIT action=%s endpoint=%s user=%s ip=%s status=%d hash=%s ts=%s",
        action, endpoint, user_id or "anonymous", ip or "unknown",
        status_code, payload_hash, datetime.utcnow().isoformat(),
    )
