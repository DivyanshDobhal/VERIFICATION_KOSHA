from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from app.database import get_db
from app.schemas.session import SessionCreate, SessionResponse
from app.services.session_service import session_service
from app.models.session import RecordingSession
from app.models.worker import Worker
from app.models.site import Site
from app.security.authorization import require_operator

router = APIRouter(prefix="/sessions", tags=["Recording Sessions"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_recording_session(
    session_in: SessionCreate,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    """Creates a new recording session permanently referencing existing Worker ID."""
    session = await session_service.create_session(db, session_in)
    
    # Load relationships for response
    stmt = (
        select(RecordingSession)
        .where(RecordingSession.id == session.id)
        .options(selectinload(RecordingSession.worker), selectinload(RecordingSession.site))
    )
    loaded = (await db.execute(stmt)).scalar_one()

    return SessionResponse(
        id=loaded.id,
        session_id=loaded.session_id,
        worker_id=loaded.worker.worker_id,
        worker_name=loaded.worker.full_name,
        site_id=loaded.site_id,
        site_name=loaded.site.site_name if loaded.site else "Site Unit",
        session_date=loaded.session_date,
        session_time=loaded.session_time,
        recognition_method=loaded.recognition_method,
        session_metadata=loaded.session_metadata,
        status=loaded.status,
        created_at=loaded.created_at,
    )

@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    site_id: Optional[uuid.UUID] = None,
    worker_id: Optional[str] = None,
    date_filter: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    query = (
        select(RecordingSession)
        .options(selectinload(RecordingSession.worker), selectinload(RecordingSession.site))
        .order_by(RecordingSession.created_at.desc())
        .limit(limit)
    )

    if site_id:
        query = query.where(RecordingSession.site_id == site_id)

    result = await db.execute(query)
    sessions = result.scalars().all()

    return [
        SessionResponse(
            id=s.id,
            session_id=s.session_id,
            worker_id=s.worker.worker_id,
            worker_name=s.worker.full_name,
            site_id=s.site_id,
            site_name=s.site.site_name if s.site else "Construction Site",
            session_date=s.session_date,
            session_time=s.session_time,
            recognition_method=s.recognition_method,
            session_metadata=s.session_metadata,
            status=s.status,
            created_at=s.created_at,
        )
        for s in sessions
    ]

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    stmt = (
        select(RecordingSession)
        .where(RecordingSession.session_id == session_id)
        .options(selectinload(RecordingSession.worker), selectinload(RecordingSession.site))
    )
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=s.id,
        session_id=s.session_id,
        worker_id=s.worker.worker_id,
        worker_name=s.worker.full_name,
        site_id=s.site_id,
        site_name=s.site.site_name if s.site else "Construction Site",
        session_date=s.session_date,
        session_time=s.session_time,
        recognition_method=s.recognition_method,
        session_metadata=s.session_metadata,
        status=s.status,
        created_at=s.created_at,
    )
