import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, Date, Time, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class RecordingSession(Base):
    __tablename__ = "recording_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, unique=True, nullable=False, index=True) # SES-XXXX
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="RESTRICT"), nullable=False, index=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="RESTRICT"), nullable=False, index=True)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=True)
    session_date = Column(Date, default=date.today, nullable=False)
    session_time = Column(Time, default=datetime.utcnow().time, nullable=False)
    recognition_method = Column(String, default="Fingerprint Biometric - Optical 500DPI")
    session_metadata = Column(JSONB, default=dict)
    idempotency_key = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="Verified & Active") # 'Verified & Active', 'Completed', 'Safety Flagged'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    worker = relationship("Worker", back_populates="recording_sessions")
    site = relationship("Site")
    operator = relationship("Operator")
