from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class BiometricEnrollRequest(BaseModel):
    worker_id: str = Field(..., description="Permanent Worker ID (e.g. WK-1001)")
    finger_type: str = Field(..., description="e.g. 'Right Thumb', 'Right Index'")
    fingerprint_image_base64: str = Field(..., description="Base64 encoded scanner image (PNG/BMP/WSQ)")
    consent_reference_id: Optional[uuid.UUID] = None
    min_quality_threshold: Optional[float] = 60.0

class BiometricEnrollResponse(BaseModel):
    status: str # SUCCESS, MODEL_NOT_CONFIGURED, QUALITY_TOO_LOW
    worker_id: str
    finger_type: str
    quality_score: float
    model_version: str
    template_id: Optional[uuid.UUID] = None
    message: str

class BiometricCompareRequest(BaseModel):
    image_a_base64: str
    image_b_base64: str

class BiometricCompareResponse(BaseModel):
    similarity: float
    match: bool
    threshold_applied: float
    model_version: str
