import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Worker(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(String, unique=True, nullable=False, index=True) # Permanent Worker ID (WK-XXXX)
    full_name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    weight = Column(Numeric(5, 2), nullable=False)
    gender = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    department = Column(String, nullable=False)
    worker_category = Column(String, nullable=False)
    additional_metadata = Column(JSONB, default=dict)
    registration_date = Column(Date, default=date.today)
    status = Column(String, default="active") # active, inactive, under_review
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    biometric_templates = relationship("BiometricTemplate", back_populates="worker", cascade="all, delete-orphan")
    recording_sessions = relationship("RecordingSession", back_populates="worker")
    consents = relationship("BiometricConsent", back_populates="worker", cascade="all, delete-orphan")
