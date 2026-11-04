"""
FastAPI REST API Service for KOSHA LABS Biometric Fingerprint Recognition.
Provides endpoints for:
- Worker Enrollment (with duplicate detection & prevention)
- 1:1 Biometric Verification (image-to-image or image-to-worker)
- 1:N Biometric Identification (retrieving worker identity from gallery)
- Multi-session biometric registration
- Numerical embedding extraction
- System health & gallery status
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf

from config.settings import CHECKPOINTS_DIR, GALLERY_STORE_DIR
from src.preprocessing.pipeline import FingerprintPreprocessor
from src.models.siamese_cnn import build_base_cnn
from src.service.gallery import BiometricGallery
from src.service.threshold import ThresholdOptimizer

app = FastAPI(
    title="KOSHA LABS – Biometric Fingerprint Recognition API",
    description="Enterprise biometric identification and verification REST microservice powered by Siamese CNN.",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service Singletons
preprocessor = FingerprintPreprocessor()
threshold_opt = ThresholdOptimizer(CHECKPOINTS_DIR / "calibrated_thresholds.json")
gallery = BiometricGallery(GALLERY_STORE_DIR / "kosha_gallery.json")

# Global feature extractor model
feature_extractor: Optional[tf.keras.Model] = None


def get_feature_extractor() -> tf.keras.Model:
    """Loads feature extractor with weights."""
    global feature_extractor
    if feature_extractor is None:
        base = build_base_cnn(input_shape=(128, 128, 1), embedding_dim=128)
        # Check for saved weights
        ckpt_path = CHECKPOINTS_DIR / "siamese_cnn_final.weights.h5"
        if not ckpt_path.exists():
            # Check for fold checkpoints
            fold_ckpts = list(CHECKPOINTS_DIR.glob("fold_*_best_siamese_model.weights.h5"))
            if fold_ckpts:
                ckpt_path = fold_ckpts[0]
            else:
                ckpt_path = CHECKPOINTS_DIR / "best_siamese_model.weights.h5"

        if ckpt_path.exists():
            try:
                # Load weights into dummy full siamese or extract base layer weights
                from src.models.siamese_cnn import build_siamese_network
                full_siamese, base_sub = build_siamese_network()
                full_siamese.load_weights(str(ckpt_path))
                base = base_sub
                print(f"[API] Loaded feature extractor weights from: {ckpt_path}")
            except Exception as e:
                print(f"[API] Warning loading weights ({e}); using initialized feature extractor.")
        else:
            print("[API] Notice: No weights file found; feature extractor initialized.")

        feature_extractor = base
    return feature_extractor


def extract_embedding_from_bytes(file_bytes: bytes) -> np.ndarray:
    """Helper to preprocess uploaded image bytes and generate 128-D embedding."""
    model = get_feature_extractor()
    img_gray = preprocessor.load_image(file_bytes)
    is_valid, quality_score, msg = preprocessor.validate_quality(img_gray)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image quality validation failed: {msg}",
        )

    processed_tensor = preprocessor.process_image(img_gray, return_tensor=False)
    batch = np.expand_dims(processed_tensor, axis=0)  # Shape (1, 128, 128, 1)
    embedding = model.predict(batch, verbose=0)[0]  # Shape (128,)
    # Ensure exact unit normalization
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


@app.get("/health", tags=["System"])
def health_check():
    """System status and runtime biometric configuration."""
    model = get_feature_extractor()
    return {
        "status": "HEALTHY",
        "system": "KOSHA LABS Biometric Fingerprint Recognition",
        "model_architecture": "Siamese CNN (4-Block Conv + L2-Normalized 128-D Embedding)",
        "total_enrolled_workers": len(gallery.workers),
        "total_enrolled_sessions": sum(len(w["sessions"]) for w in gallery.workers.values()),
        "operational_thresholds": threshold_opt.thresholds,
    }


@app.post("/enroll", tags=["Biometric Enrollment"], status_code=status.HTTP_201_CREATED)
async def enroll_worker(
    worker_id: str = Form(..., description="Unique permanent Worker ID (e.g. EMP-1001)"),
    name: str = Form(..., description="Full Name of the worker"),
    department: Optional[str] = Form("General", description="Department / Division"),
    finger_label: Optional[str] = Form("Right_index_finger", description="Finger anatomical identifier"),
    fingerprint_image: UploadFile = File(..., description="Fingerprint image file (BMP, PNG, JPG)"),
):
    """
    Enrolls a new worker with duplicate detection.
    Blocks registration if the biometric fingerprint matches an existing enrolled worker.
    """
    file_bytes = await fingerprint_image.read()
    embedding = extract_embedding_from_bytes(file_bytes)

    dup_thresh = threshold_opt.thresholds.get("duplicate_prevention_threshold", 0.70)
    result = gallery.enroll_worker(
        worker_id=worker_id,
        name=name,
        embedding=embedding,
        finger_label=finger_label or "primary_finger",
        metadata={"department": department},
        duplicate_threshold=dup_thresh,
    )

    if not result["success"]:
        if result.get("error") == "DUPLICATE_REGISTRATION_PREVENTED":
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=result,
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))

    return result


@app.post("/sessions", tags=["Biometric Enrollment"])
async def add_session(
    worker_id: str = Form(..., description="Permanent Worker ID"),
    finger_label: str = Form("Left_thumb_finger", description="Finger identifier for this session"),
    notes: Optional[str] = Form("", description="Session capture notes or date"),
    fingerprint_image: UploadFile = File(..., description="Fingerprint image file"),
):
    """
    Appends an additional biometric capture session for an existing permanent Worker ID.
    Supports multi-finger enrollment and scheduled recertifications.
    """
    file_bytes = await fingerprint_image.read()
    embedding = extract_embedding_from_bytes(file_bytes)

    result = gallery.add_recording_session(
        worker_id=worker_id,
        embedding=embedding,
        finger_label=finger_label,
        session_notes=notes,
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))

    return result


@app.post("/verify", tags=["1:1 Verification"])
async def verify_fingerprint(
    worker_id: Optional[str] = Form(None, description="Enrolled Worker ID (if verifying image against worker)"),
    fingerprint_image: UploadFile = File(..., description="Primary fingerprint image"),
    secondary_image: Optional[UploadFile] = File(None, description="Secondary image (if verifying image A vs image B)"),
    security_level: Optional[str] = Form("standard", description="Security mode: 'standard' (FAR<=1%) or 'strict' (FAR<=0.1%)"),
):
    """
    1:1 Biometric Verification.
    Supports:
    1. Verifying an uploaded probe against an enrolled Worker ID.
    2. Verifying two directly uploaded fingerprint images against each other.
    """
    primary_bytes = await fingerprint_image.read()
    emb1 = extract_embedding_from_bytes(primary_bytes)

    # Determine decision threshold
    if security_level == "strict":
        threshold = threshold_opt.thresholds.get("strict_far_01_threshold", 0.0150)
    else:
        threshold = threshold_opt.thresholds.get("standard_far_1_threshold", 0.0200)

    if secondary_image is not None:
        # Image-to-Image 1:1 verification
        sec_bytes = await secondary_image.read()
        emb2 = extract_embedding_from_bytes(sec_bytes)

        distance = float(np.linalg.norm(emb1 - emb2))
        is_verified = distance <= threshold
        confidence = float(max(0.0, min(1.0, 1.0 - (distance / (threshold * 2.0)))))

        return {
            "mode": "image_to_image_verification",
            "verified": is_verified,
            "euclidean_distance": distance,
            "decision_threshold": threshold,
            "security_level": security_level,
            "confidence_score": confidence,
            "decision": "MATCH_CONFIRMED" if is_verified else "NON_MATCH",
        }
    elif worker_id:
        # Worker-to-Image 1:1 verification
        res = gallery.verify_worker(worker_id=worker_id, probe_embedding=emb1, threshold=threshold)
        if "error" in res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=res["error"])
        res["security_level"] = security_level
        res["decision"] = "MATCH_CONFIRMED" if res["verified"] else "NON_MATCH"
        return res
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either worker_id or secondary_image for 1:1 verification.",
        )


@app.post("/identify", tags=["1:N Biometric Identification"])
async def identify_probe(
    fingerprint_image: UploadFile = File(..., description="Query probe fingerprint image"),
    top_k: int = Query(5, ge=1, le=20, description="Number of top candidates to retrieve"),
):
    """
    1:N Biometric Search & Worker Identification.
    Searches the entire biometric gallery to find matching worker identities.
    """
    file_bytes = await fingerprint_image.read()
    probe_emb = extract_embedding_from_bytes(file_bytes)

    threshold = threshold_opt.thresholds.get("eer_threshold", 0.0235)
    result = gallery.identify_probe(probe_embedding=probe_emb, top_k=top_k, threshold=threshold)
    return result


@app.post("/embeddings", tags=["Biometric Feature Extraction"])
async def generate_embedding(
    fingerprint_image: UploadFile = File(..., description="Input fingerprint image"),
):
    """
    Generates numerical 128-dimensional L2-normalized embedding vector.
    """
    file_bytes = await fingerprint_image.read()
    emb = extract_embedding_from_bytes(file_bytes)
    return {
        "embedding_dimension": len(emb),
        "l2_norm": float(np.linalg.norm(emb)),
        "embedding_vector": emb.tolist(),
    }


@app.get("/workers", tags=["Biometric Gallery"])
def list_enrolled_workers():
    """Lists all enrolled workers and their recording sessions."""
    return {
        "total_workers": len(gallery.workers),
        "workers": gallery.list_workers(),
    }
