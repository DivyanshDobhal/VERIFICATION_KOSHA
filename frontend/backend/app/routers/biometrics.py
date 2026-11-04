from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.biometric import BiometricEnrollRequest, BiometricEnrollResponse, BiometricCompareRequest, BiometricCompareResponse
from app.schemas.recognition import RecognitionRequest, RecognitionResponse
from app.services.recognition_service import recognition_service
from app.services.encryption_service import encryption_service
from app.models.worker import Worker
from app.models.biometric import BiometricTemplate
from app.ml.preprocessing import preprocessor
from app.ml.model_loader import model_manager
from app.security.authorization import require_operator

router = APIRouter(prefix="/biometrics", tags=["Biometrics"])

@router.post("/enroll", response_model=BiometricEnrollResponse)
async def enroll_fingerprint(
    enroll_req: BiometricEnrollRequest,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    """Enrolls a fingerprint template for an existing worker."""
    # 1. Validate worker exists
    worker_stmt = select(Worker).where(Worker.worker_id == enroll_req.worker_id)
    worker = (await db.execute(worker_stmt)).scalar_one_or_none()
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker with ID '{enroll_req.worker_id}' not found.",
        )

    # 2. Decode image and check quality
    img = preprocessor.decode_base64_image(enroll_req.fingerprint_image_base64)
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid fingerprint image data.",
        )

    quality = preprocessor.assess_quality(img)
    if quality < enroll_req.min_quality_threshold:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image quality ({quality}%) is below minimum threshold ({enroll_req.min_quality_threshold}%).",
        )

    # 3. Model check (Strict: never fake embeddings if unconfigured)
    if not model_manager.is_configured():
        return BiometricEnrollResponse(
            status="MODEL_NOT_CONFIGURED",
            worker_id=worker.worker_id,
            finger_type=enroll_req.finger_type,
            quality_score=quality,
            model_version=model_manager.version,
            message="Trained Siamese CNN model weights are unconfigured. Template enrollment aborted."
        )

    # 4. Extract embedding
    tensor = preprocessor.preprocess_for_siamese_cnn(img)
    embedding_vec = model_manager.extract_128d_embedding(tensor)
    embedding_bytes = embedding_vec.tobytes()

    # 5. Encrypt with AES-256 and generate SHA-256 template hash
    encrypted_payload = encryption_service.encrypt_embedding(embedding_bytes)
    template_hash = encryption_service.generate_template_hash(embedding_bytes)

    # Check for duplicate template
    dup_stmt = select(BiometricTemplate).where(BiometricTemplate.template_hash == template_hash)
    existing_template = (await db.execute(dup_stmt)).scalar_one_or_none()
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This fingerprint pattern has already been enrolled in the identity vault.",
        )

    # 6. Store template
    template = BiometricTemplate(
        worker_id=worker.id,
        finger_type=enroll_req.finger_type,
        encrypted_embedding=encrypted_payload,
        embedding_dimension=128,
        template_hash=template_hash,
        quality_score=quality,
        model_version=model_manager.version,
        consent_record_id=enroll_req.consent_reference_id,
        status="active"
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)

    return BiometricEnrollResponse(
        status="SUCCESS",
        worker_id=worker.worker_id,
        finger_type=enroll_req.finger_type,
        quality_score=quality,
        model_version=model_manager.version,
        template_id=template.id,
        message=f"Fingerprint {enroll_req.finger_type} successfully enrolled for {worker.worker_id}."
    )

@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_worker(
    req: RecognitionRequest,
    db: AsyncSession = Depends(get_db),
    user_token: dict = Depends(require_operator)
):
    """Executes 1:N fingerprint recognition against stored encrypted templates."""
    return await recognition_service.recognize_fingerprint(db, req)
