import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.session import RecordingSession
from app.models.worker import Worker
from app.models.audit import AuditLog
from app.schemas.session import SessionCreate
from fastapi import HTTPException, status

class SessionService:
    @staticmethod
    async def generate_next_session_id(db: AsyncSession) -> str:
        result = await db.execute(select(func.count(RecordingSession.id)))
        count = result.scalar() or 0
        return f"SES-{str(count + 1).zfill(3)}"

    @classmethod
    async def create_session(
        cls, 
        db: AsyncSession, 
        session_in: SessionCreate,
        operator_id: Optional[uuid.UUID] = None
    ) -> RecordingSession:
        # 1. Idempotency Check
        existing_stmt = select(RecordingSession).where(RecordingSession.idempotency_key == session_in.idempotency_key)
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            return existing

        # 2. Verify worker exists and is active
        worker_stmt = select(Worker).where(Worker.worker_id == session_in.worker_id)
        worker = (await db.execute(worker_stmt)).scalar_one_or_none()
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Worker with permanent ID '{session_in.worker_id}' not found.",
            )

        if worker.status == "inactive":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Worker '{session_in.worker_id}' is marked inactive. Cannot log shift.",
            )

        # 3. Generate unique Session ID
        session_id_str = await cls.generate_next_session_id(db)

        # 4. Create session permanently linked to worker
        session = RecordingSession(
            session_id=session_id_str,
            worker_id=worker.id,
            site_id=session_in.site_id,
            operator_id=operator_id or session_in.operator_id,
            recognition_method=session_in.recognition_method or "Fingerprint Biometric - Optical 500DPI",
            session_metadata={
                "shift": session_in.shift,
                "gate": session_in.gate,
                "worker_permanent_id": worker.worker_id,
                **(session_in.session_metadata or {})
            },
            idempotency_key=session_in.idempotency_key,
            status="Verified & Active"
        )
        db.add(session)

        # 5. Audit log
        audit = AuditLog(
            user_id=operator_id,
            action="SESSION_LOGGED",
            entity_type="SESSION",
            entity_id=session.session_id,
            metadata={
                "worker_id": worker.worker_id,
                "shift": session_in.shift,
                "site_id": str(session_in.site_id)
            }
        )
        db.add(audit)

        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def list_worker_sessions(db: AsyncSession, worker_id: str) -> List[RecordingSession]:
        worker_stmt = select(Worker.id).where(Worker.worker_id == worker_id)
        worker_uuid = (await db.execute(worker_stmt)).scalar_one_or_none()
        if not worker_uuid:
            return []

        query = (
            select(RecordingSession)
            .where(RecordingSession.worker_id == worker_uuid)
            .order_by(RecordingSession.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()

session_service = SessionService()
