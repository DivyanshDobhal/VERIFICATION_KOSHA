import uuid
import numpy as np
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.biometric import BiometricTemplate
from app.models.worker import Worker
from app.models.recognition import RecognitionLog
from app.models.site import Site
from app.schemas.recognition import RecognitionRequest, RecognitionResponse, CandidateMatch
from app.ml.preprocessing import preprocessor
from app.ml.model_loader import model_manager
from app.ml.matcher import matcher
from app.services.encryption_service import encryption_service
from app.config import settings
from fastapi import HTTPException, status

class RecognitionService:
    @classmethod
    async def recognize_fingerprint(
        cls, 
        db: AsyncSession, 
        req: RecognitionRequest, 
        operator_id: Optional[uuid.UUID] = None
    ) -> RecognitionResponse:
        # 1. Decode & Preprocess Image
        img = preprocessor.decode_base64_image(req.fingerprint_image_base64)
        if img is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid or unreadable fingerprint image stream.",
            )

        # 2. Check Image Quality
        quality = preprocessor.assess_quality(img)
        if quality < 30.0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Fingerprint quality ({quality}%) is too degraded. Please clean sensor and retry.",
            )

        # 3. Model availability check
        if not model_manager.is_configured():
            # Return explicit service unavailable response as strictly required by prompt
            return RecognitionResponse(
                status="SERVICE_UNAVAILABLE",
                message="Trained Siamese CNN biometric model is not configured. Biometric matching unavailable.",
                verification_required=False,
            )

        # 4. Generate 128D Embedding
        tensor = preprocessor.preprocess_for_siamese_cnn(img)
        query_embedding = model_manager.extract_128d_embedding(tensor)

        # 5. Retrieve Enrolled Gallery (Trusted Backend in-memory decryption)
        templates_stmt = (
            select(BiometricTemplate)
            .where(BiometricTemplate.status == "active")
            .options(selectinload(BiometricTemplate.worker))
        )
        templates = (await db.execute(templates_stmt)).scalars().all()

        gallery = []
        for t in templates:
            try:
                decrypted_bytes = encryption_service.decrypt_embedding(t.encrypted_embedding)
                vector = np.frombuffer(decrypted_bytes, dtype=np.float32)
                gallery.append({
                    "template_id": t.id,
                    "worker_id": t.worker.worker_id,
                    "worker_name": t.worker.full_name,
                    "department": t.worker.department,
                    "worker_uuid": t.worker.id,
                    "embedding": vector,
                })
            except Exception:
                continue

        # 6. Execute 1:N Gallery Search
        result_status, top_matches, best_score = matcher.match_one_to_n(query_embedding, gallery)

        candidates = [
            CandidateMatch(
                worker_id=m["worker_id"],
                worker_name=m["worker_name"],
                department=m["department"],
                similarity_score=m["similarity_score"]
            )
            for m in top_matches
        ]

        review_id_generated = None
        matched_worker_id = None
        verification_required = False

        if result_status == "MATCH":
            matched_worker_id = top_matches[0]["worker_id"]
            matched_worker_name = top_matches[0]["worker_name"]
            verification_required = False
        elif result_status == "UNCERTAIN":
            verification_required = True
            # Create review log entry
            log = RecognitionLog(
                operator_id=operator_id or req.operator_id,
                site_id=req.site_id,
                scanned_finger=req.scanned_finger or "Right Thumb",
                result_status="UNCERTAIN",
                confidence_score=best_score * 100.0,
                matched_worker_id=gallery[0]["worker_uuid"] if gallery else None,
                review_status="pending",
                model_version=settings.MODEL_VERSION,
                review_notes="Low similarity match routed to supervisor review."
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            review_id_generated = log.review_id

        # Return standardized response according to Section 8 specifications
        return RecognitionResponse(
            status=result_status,
            worker_id=matched_worker_id,
            worker_name=matched_worker_name if result_status == "MATCH" else None,
            confidence_score=round(best_score * 100.0, 2),
            verification_required=verification_required,
            candidates=candidates,
            review_id=review_id_generated,
        )

recognition_service = RecognitionService()
