import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update, delete
from sqlalchemy.orm import selectinload
from app.models.worker import Worker
from app.models.biometric import BiometricTemplate
from app.models.consent import BiometricConsent
from app.models.audit import AuditLog
from app.schemas.worker import WorkerCreate, WorkerUpdate
from fastapi import HTTPException, status

class WorkerService:
    @staticmethod
    async def generate_next_worker_id(db: AsyncSession) -> str:
        """Atomically gets next formatted permanent Worker ID"""
        result = await db.execute(select(func.count(Worker.id)))
        count = result.scalar() or 0
        return f"WK-{1001 + count}"

    @classmethod
    async def create_worker(
        cls, 
        db: AsyncSession, 
        worker_in: WorkerCreate, 
        operator_id: Optional[uuid.UUID] = None
    ) -> Worker:
        # Enforce consent validation
        if not worker_in.consent_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Biometric consent is mandatory to register worker identity.",
            )

        # Generate permanent Worker ID
        worker_id_str = await cls.generate_next_worker_id(db)

        # Create worker record
        worker = Worker(
            worker_id=worker_id_str,
            full_name=worker_in.full_name,
            age=worker_in.age,
            weight=worker_in.weight,
            gender=worker_in.gender,
            contact_number=worker_in.contact_number,
            emergency_contact=worker_in.emergency_contact,
            blood_group=worker_in.blood_group,
            site_id=worker_in.site_id,
            department=worker_in.department,
            worker_category=worker_in.worker_category,
            additional_metadata=worker_in.additional_metadata or {},
            status="active"
        )
        db.add(worker)
        await db.flush()

        # Create consent record
        consent = BiometricConsent(
            worker_id=worker.id,
            consent_status=True,
            consent_version="v2.4",
            purpose="Industrial deduplication & attendance authentication"
        )
        db.add(consent)

        # Record audit log
        audit = AuditLog(
            user_id=operator_id,
            action="WORKER_REGISTERED",
            entity_type="WORKER",
            entity_id=worker.worker_id,
            metadata={"worker_name": worker.full_name, "department": worker.department}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(worker)
        return worker

    @staticmethod
    async def get_worker_by_worker_id(db: AsyncSession, worker_id: str) -> Optional[Worker]:
        query = (
            select(Worker)
            .where(Worker.worker_id == worker_id)
            .options(selectinload(Worker.biometric_templates), selectinload(Worker.recording_sessions))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_workers(
        db: AsyncSession, 
        search: Optional[str] = None, 
        site_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> Tuple[List[Worker], int]:
        query = select(Worker).options(selectinload(Worker.biometric_templates))

        if search:
            search_fmt = f"%{search}%"
            query = query.where(
                or_(
                    Worker.full_name.ilike(search_fmt),
                    Worker.worker_id.ilike(search_fmt),
                    Worker.department.ilike(search_fmt)
                )
            )
        if site_id:
            query = query.where(Worker.site_id == site_id)
        if status_filter and status_filter != "ALL":
            query = query.where(Worker.status == status_filter)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Paginated items
        items_query = query.offset(skip).limit(limit).order_by(Worker.worker_id.asc())
        result = await db.execute(items_query)
        return result.scalars().all(), total

worker_service = WorkerService()
