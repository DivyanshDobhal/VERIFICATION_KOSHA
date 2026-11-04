import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class RecognitionLog(Base):
    __tablename__ = "recognition_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(String, unique=True, nullable=True) # REV-XXX
    operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    scanned_finger = Column(String, nullable=False)
    recognition_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    result_status = Column(String, nullable=False) # 'MATCH', 'UNCERTAIN', 'NO_MATCH', 'ERROR'
    confidence_score = Column(Numeric(5, 2), nullable=True)
    matched_worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id"), nullable=True)
    secondary_candidate_id = Column(UUID(as_uuid=True), ForeignKey("workers.id"), nullable=True)
    review_status = Column(String, default="pending") # 'pending', 'approved', 'rejected', 'recaptured'
    model_version = Column(String, default="kosha-siamese-v1.4")
    review_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=True)
