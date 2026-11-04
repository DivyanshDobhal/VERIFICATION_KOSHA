import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class BiometricConsent(Base):
    __tablename__ = "biometric_consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    consent_status = Column(Boolean, default=True, nullable=False)
    consent_version = Column(String, default="v2.4", nullable=False)
    consent_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    purpose = Column(String, default="Industrial deduplication & attendance authentication")
    withdrawal_timestamp = Column(DateTime, nullable=True)

    worker = relationship("Worker", back_populates="consents")
