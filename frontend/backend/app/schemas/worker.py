from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import uuid

class WorkerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    age: int = Field(..., ge=18, le=75)
    weight: float = Field(..., ge=35.0, le=180.0)
    gender: Optional[str] = "Prefer not to say"
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = "B+"
    site_id: Optional[uuid.UUID] = None
    department: str
    worker_category: str
    additional_metadata: Optional[Dict[str, Any]] = {}

class WorkerCreate(WorkerBase):
    fingerprint_image: Optional[str] = None # Base64 scanner image for pre-registration deduplication check
    finger_type: Optional[str] = "Right Thumb"
    consent_accepted: bool = Field(..., description="Worker informed biometric consent")

class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    worker_category: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class EnrolledFingerMetadata(BaseModel):
    finger_type: str
    quality_score: float
    model_version: str
    created_at: datetime
    status: str

class WorkerResponse(WorkerBase):
    id: uuid.UUID
    worker_id: str
    registration_date: date
    status: str
    created_at: datetime
    updated_at: datetime
    enrolled_finger_count: Optional[int] = 0
    enrolled_fingers: Optional[List[EnrolledFingerMetadata]] = []

    class Config:
        from_attributes = True

class WorkerListResponse(BaseModel):
    items: List[WorkerResponse]
    total: int
    page: int
    size: int
