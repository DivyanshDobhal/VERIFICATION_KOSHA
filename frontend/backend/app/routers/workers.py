from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid
from app.database import get_db
from app.schemas.worker import (
    WorkerCreate,
    WorkerUpdate,
    WorkerResponse,
    WorkerListResponse,
    EnrolledFingerMetadata
)
from app.services.worker_service import worker_service
from app.services.session_service import session_service
from app.schemas.session import SessionResponse
from app.security.authorization import require_operator, require_supervisor

router = APIRouter(prefix="/workers", tags=["Workers"])

@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
async def register_worker(
    worker_in: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    """Registers new worker identity. Enforces informed biometric consent and single permanent ID."""
    created = await worker_service.create_worker(db, worker_in)
    return created

@router.get("", response_model=WorkerListResponse)
async def list_workers(
    search: Optional[str] = None,
    site_id: Optional[uuid.UUID] = None,
    status: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    skip = (page - 1) * size
    items, total = await worker_service.list_workers(
        db, search=search, site_id=site_id, status_filter=status, skip=skip, limit=size
    )
    return WorkerListResponse(items=items, total=total, page=page, size=size)

@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    worker = await worker_service.get_worker_by_worker_id(db, worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID '{worker_id}' not found.",
        )
    return worker

@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: str,
    worker_update: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_supervisor)
):
    worker = await worker_service.get_worker_by_worker_id(db, worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID '{worker_id}' not found.",
        )

    for field, value in worker_update.dict(exclude_unset=True).items():
        setattr(worker, field, value)

    await db.commit()
    await db.refresh(worker)
    return worker

@router.delete("/{worker_id}")
async def deactivate_worker(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_supervisor)
):
    worker = await worker_service.get_worker_by_worker_id(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.status = "inactive"
    await db.commit()
    return {"message": f"Worker {worker_id} successfully deactivated."}

@router.get("/{worker_id}/sessions")
async def get_worker_sessions(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    """Retrieves all historical recording sessions linked to this single permanent Worker ID."""
    sessions = await session_service.list_worker_sessions(db, worker_id)
    return sessions

@router.get("/{worker_id}/biometrics", response_model=List[EnrolledFingerMetadata])
async def get_worker_biometric_metadata(
    worker_id: str,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    """Returns permitted enrollment metadata only; NEVER exposes raw biometric embeddings."""
    worker = await worker_service.get_worker_by_worker_id(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    return [
        EnrolledFingerMetadata(
            finger_type=t.finger_type,
            quality_score=float(t.quality_score),
            model_version=t.model_version,
            created_at=t.created_at,
            status=t.status
        )
        for t in worker.biometric_templates
    ]
