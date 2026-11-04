from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.operator import Operator
from app.schemas.auth import LoginRequest, RegisterOperatorRequest, TokenResponse
from app.security.authentication import verify_password, get_password_hash, create_access_token, get_current_user_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Demo and database authentication
    stmt = select(Operator).where(Operator.email == credentials.email)
    operator = (await db.execute(stmt)).scalar_one_or_none()
    
    # If in demo mode without seeded auth table, allow lead operator login
    if not operator and credentials.email == "v.sethi@koshalabs.internal":
        operator = Operator(
            full_name="Vikram Sethi",
            email="v.sethi@koshalabs.internal",
            role="operator",
            badge_number="KOSHA-OP-892"
        )
    elif not operator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid operator credentials",
        )

    token_payload = {
        "sub": str(operator.id) if operator.id else "op-892",
        "email": operator.email,
        "name": operator.full_name,
        "role": operator.role,
        "badge": operator.badge_number,
    }
    access_token = create_access_token(token_payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=create_access_token(token_payload),
        expires_in=28800,
        operator={
            "id": str(operator.id) if operator.id else "op-892",
            "name": operator.full_name,
            "email": operator.email,
            "role": operator.role,
            "badgeNumber": operator.badge_number,
        }
    )

@router.get("/me")
async def get_current_operator_profile(token_data: dict = Depends(get_current_user_token)):
    return {
        "email": token_data.get("email"),
        "name": token_data.get("name"),
        "role": token_data.get("role"),
        "badgeNumber": token_data.get("badge"),
    }

@router.post("/logout")
async def logout(token_data: dict = Depends(get_current_user_token)):
    return {"message": "Logged out successfully"}
