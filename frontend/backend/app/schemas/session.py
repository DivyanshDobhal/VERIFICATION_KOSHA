from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, time, datetime
import uuid

class SessionCreate(BaseModel):
    worker_id: str = Field(..., description="Permanent Worker ID (WK-XXXX)")
    site_id: uuid.UUID
    operator_id: Optional[uuid.UUID] = None
    shift: Optional[str] = "Morning Shift (06:00 - 14:00)"
    gate: Optional[str] = "North Gate Turnstile 2"
    recognition_method: Optional[str] = "Fingerprint Biometric - Optical 500DPI"
    session_metadata: Optional[Dict[str, Any]] = {}
    idempotency_key: str = Field(..., description="Unique client key preventing duplicate shift creation")

class SessionResponse(BaseModel):
    id: uuid.UUID
    session_id: str
    worker_id: str
    worker_name: str
    site_id: uuid.UUID
    site_name: Optional[str] = None
    session_date: date
    session_time: time
    recognition_method: str
    session_metadata: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
