from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.recognition import RecognitionLog
from app.models.audit import AuditLog
from app.security.authorization import require_supervisor

router = APIRouter(prefix="/recognition/reviews", tags=["Recognition Reviews"])

@router.get("")
async def list_recognition_reviews(
    review_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_supervisor)
):
    query = select(RecognitionLog).order_by(RecognitionLog.recognition_timestamp.desc())
    if review_status:
        query = query.where(RecognitionLog.review_status == review_status)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{review_id}/approve")
async def approve_review(
    review_id: str,
    notes: Optional[str] = "Supervisor verified identity match",
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_supervisor)
):
    stmt = select(RecognitionLog).where(RecognitionLog.review_id == review_id)
    log = (await db.execute(stmt)).scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Review entry not found")

    log.review_status = "approved"
    log.review_notes = notes
    log.resolved_at = datetime.utcnow()

    # Audit log
    audit = AuditLog(
        action="RECOGNITION_REVIEW_APPROVED",
        entity_type="REVIEW",
        entity_id=review_id,
        metadata={"reviewer": user_token.get("name"), "notes": notes}
    )
    db.add(audit)
    await db.commit()
    return {"message": f"Review {review_id} approved. Identity confirmed."}

@router.post("/{review_id}/reject")
async def reject_review(
    review_id: str,
    notes: Optional[str] = "Supervisor rejected false match",
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_supervisor)
):
    stmt = select(RecognitionLog).where(RecognitionLog.review_id == review_id)
    log = (await db.execute(stmt)).scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Review entry not found")

    log.review_status = "rejected"
    log.review_notes = notes
    log.resolved_at = datetime.utcnow()

    audit = AuditLog(
        action="RECOGNITION_REVIEW_REJECTED",
        entity_type="REVIEW",
        entity_id=review_id,
        metadata={"reviewer": user_token.get("name"), "notes": notes}
    )
    db.add(audit)
    await db.commit()
    return {"message": f"Review {review_id} rejected. Discrepancy logged."}

@router.post("/{review_id}/request-recapture")
async def recapture_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_supervisor)
):
    stmt = select(RecognitionLog).where(RecognitionLog.review_id == review_id)
    log = (await db.execute(stmt)).scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Review entry not found")

    log.review_status = "recaptured"
    log.resolved_at = datetime.utcnow()
    await db.commit()
    return {"message": f"Recapture requested for review {review_id}."}
