from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterOperatorRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "operator" # 'admin', 'operator', 'supervisor'
    badge_number: str
    assigned_site_id: Optional[uuid.UUID] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    operator: dict
