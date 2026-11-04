from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

class CandidateMatch(BaseModel):
    worker_id: str
    worker_name: str
    department: str
    site_name: Optional[str] = None
    similarity_score: float # 0.0 - 1.0

class RecognitionRequest(BaseModel):
    fingerprint_image_base64: str = Field(..., description="Captured image from optical/capacitive scanner")
    scanned_finger: Optional[str] = "Right Thumb"
    site_id: uuid.UUID
    operator_id: Optional[uuid.UUID] = None
    request_id: Optional[str] = None

class RecognitionResponse(BaseModel):
    status: str # 'MATCH' | 'UNCERTAIN' | 'NO_MATCH' | 'SERVICE_UNAVAILABLE'
    worker_id: Optional[str] = None
    worker_name: Optional[str] = None
    confidence_score: Optional[float] = None
    verification_required: bool = False
    candidates: Optional[List[CandidateMatch]] = []
    message: Optional[str] = None
    review_id: Optional[str] = None

class ReviewActionRequest(BaseModel):
    review_id: str
    decision: str # 'approve' | 'reject' | 'recapture'
    notes: Optional[str] = None
    confirmed_worker_id: Optional[str] = None
