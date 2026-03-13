import logging
from flask import request
from src.backend import db
from src.backend.models.user import AuditLog

logger = logging.getLogger(__name__)


def log_audit(action, entity_type=None, entity_id=None, user_id=None, details=None):
    """
    ADT crosscut: write an audit record for every significant action.
    ExHL crosscut: swallow DB errors so they never break main flow.
    """
    try:
        ip = request.remote_addr if request else None
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip,
            details=details or {}
        )
        db.session.add(entry)
        db.session.commit()
        logger.info("AUDIT | %s | entity=%s id=%s user=%s ip=%s",
                    action, entity_type, entity_id, user_id, ip)
    except Exception as exc:
        # ExHL: log error but don't raise — audit must never break the request
        logger.error("AuditLog write failed: %s", exc)
        db.session.rollback()