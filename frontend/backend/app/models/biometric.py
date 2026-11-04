import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class BiometricTemplate(Base):
    __tablename__ = "biometric_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    finger_type = Column(String, nullable=False) # 'Right Thumb', 'Right Index', etc.
    encrypted_embedding = Column(LargeBinary, nullable=False) # AES-256 encrypted vector
    embedding_dimension = Column(Integer, default=128)
    template_hash = Column(String, unique=True, nullable=False, index=True)
    quality_score = Column(Numeric(5, 2), nullable=False)
    model_version = Column(String, default="kosha-siamese-v1.4")
    consent_record_id = Column(UUID(as_uuid=True), ForeignKey("biometric_consents.id"), nullable=True)
    status = Column(String, default="active") # active, revoked
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    worker = relationship("Worker", back_populates="biometric_templates")
