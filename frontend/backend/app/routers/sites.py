from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.site import Site
from app.security.authorization import require_operator

router = APIRouter(prefix="/sites", tags=["Sites"])

@router.get("")
async def list_sites(
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    result = await db.execute(select(Site))
    return result.scalars().all()
