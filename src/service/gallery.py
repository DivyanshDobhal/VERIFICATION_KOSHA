"""
Persistent biometric gallery store for worker identities.
Supports:
1. Worker enrollment with metadata.
2. Duplicate registration prevention (blocks enrollment if biometrics match existing worker).
3. Multi-session biometric recordings for one permanent Worker ID.
4. 1:1 verification and 1:N biometric identification.
5. Disk persistence (JSON / SQLite).
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
import time
import numpy as np


class BiometricGallery:
    """
    Biometric Gallery Database for KOSHA LABS worker verification system.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("./gallery_store/kosha_gallery.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        # {worker_id: {"name": str, "metadata": dict, "sessions": [{"session_id": str, "finger": str, "embedding": list, "timestamp": str}]}}
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.load()

    def check_duplicate(
        self,
        probe_embedding: np.ndarray,
        duplicate_threshold: float = 0.020,
    ) -> Tuple[bool, Optional[str], float]:
        """
        Searches all enrolled embeddings to detect if probe belongs to an already registered worker.
        Returns:
            (is_duplicate, matched_worker_id, min_distance)
        """
        all_embeddings, worker_ids = self._get_all_gallery_embeddings()
        if len(worker_ids) == 0:
            return False, None, float("inf")

        # Probe shape (128,)
        diffs = all_embeddings - probe_embedding
        dists = np.linalg.norm(diffs, axis=1)

        min_idx = int(np.argmin(dists))
        min_dist = float(dists[min_idx])
        matched_worker = worker_ids[min_idx]

        is_duplicate = min_dist < duplicate_threshold
        return is_duplicate, matched_worker if is_duplicate else None, min_dist

    def enroll_worker(
        self,
        worker_id: str,
        name: str,
        embedding: np.ndarray,
        finger_label: str = "primary_finger",
        metadata: Optional[Dict[str, Any]] = None,
        duplicate_threshold: float = 0.020,
    ) -> Dict[str, Any]:
        """
        Enrolls a new worker.
        Rejects enrollment if duplicate biometrics are detected.
        """
        worker_id = str(worker_id).strip()
        if worker_id in self.workers:
            return {
                "success": False,
                "error": f"Worker ID '{worker_id}' is already registered. Use /sessions to add subsequent recordings.",
            }

        # Check for biometric duplicates
        is_dup, matched_id, min_dist = self.check_duplicate(embedding, duplicate_threshold)
        if is_dup:
            return {
                "success": False,
                "error": "DUPLICATE_REGISTRATION_PREVENTED",
                "message": f"Biometric fingerprint matches existing worker '{matched_id}' (Euclidean distance: {min_dist:.4f} < {duplicate_threshold:.4f}). Duplicate registration blocked.",
                "matched_worker_id": matched_id,
                "distance": min_dist,
            }

        # Create worker record
        session_record = {
            "session_id": f"sess_{int(time.time()*1000)}",
            "finger_label": finger_label,
            "embedding": embedding.tolist(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        self.workers[worker_id] = {
            "worker_id": worker_id,
            "name": name,
            "metadata": metadata or {},
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sessions": [session_record],
        }

        self.save()
        return {
            "success": True,
            "worker_id": worker_id,
            "name": name,
            "session_id": session_record["session_id"],
            "message": "Worker enrolled successfully.",
        }

    def add_recording_session(
        self,
        worker_id: str,
        embedding: np.ndarray,
        finger_label: str = "additional_finger",
        session_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Adds a new fingerprint recording session for an existing permanent Worker ID.
        Supports multi-finger enrollments and periodic re-scans.
        """
        worker_id = str(worker_id).strip()
        if worker_id not in self.workers:
            return {
                "success": False,
                "error": f"Worker ID '{worker_id}' does not exist.",
            }

        session_record = {
            "session_id": f"sess_{int(time.time()*1000)}",
            "finger_label": finger_label,
            "embedding": embedding.tolist(),
            "session_notes": session_notes or "",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        self.workers[worker_id]["sessions"].append(session_record)
        self.save()

        return {
            "success": True,
            "worker_id": worker_id,
            "total_sessions": len(self.workers[worker_id]["sessions"]),
            "session_id": session_record["session_id"],
            "message": "New recording session appended successfully.",
        }

    def verify_worker(
        self,
        worker_id: str,
        probe_embedding: np.ndarray,
        threshold: float = 0.020,
    ) -> Dict[str, Any]:
        """
        1:1 Verification: Verifies probe embedding against all enrolled sessions for worker_id.
        """
        worker_id = str(worker_id).strip()
        if worker_id not in self.workers:
            return {
                "verified": False,
                "error": f"Worker ID '{worker_id}' not found in gallery.",
            }

        worker = self.workers[worker_id]
        distances = []
        for sess in worker["sessions"]:
            enrolled_emb = np.array(sess["embedding"], dtype=np.float32)
            d = float(np.linalg.norm(enrolled_emb - probe_embedding))
            distances.append((d, sess["finger_label"], sess["session_id"]))

        # Best match across worker's sessions
        distances.sort(key=lambda x: x[0])
        min_dist, matched_finger, matched_session = distances[0]

        is_verified = min_dist <= threshold
        confidence = float(max(0.0, min(1.0, 1.0 - (min_dist / (threshold * 2.0)))))

        return {
            "verified": is_verified,
            "worker_id": worker_id,
            "name": worker["name"],
            "distance": min_dist,
            "threshold": threshold,
            "confidence_score": confidence,
            "matched_finger": matched_finger,
            "matched_session_id": matched_session,
        }

    def identify_probe(
        self,
        probe_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0235,
    ) -> Dict[str, Any]:
        """
        1:N Biometric Identification:
        Searches entire gallery and retrieves Rank-1 match and Top-K candidates.
        """
        all_embeddings, worker_ids = self._get_all_gallery_embeddings()
        if len(worker_ids) == 0:
            return {
                "identified": False,
                "message": "Gallery is empty. No enrolled workers.",
                "candidates": [],
            }

        diffs = all_embeddings - probe_embedding
        dists = np.linalg.norm(diffs, axis=1)

        # Sort all gallery entries by distance ascending
        sorted_indices = np.argsort(dists)

        # Aggregate by worker (best session per worker)
        seen_workers = set()
        candidates = []

        for idx in sorted_indices:
            w_id = worker_ids[idx]
            if w_id in seen_workers:
                continue
            seen_workers.add(w_id)
            d = float(dists[idx])
            w_info = self.workers[w_id]
            conf = float(max(0.0, min(1.0, 1.0 - (d / (threshold * 2.0)))))
            candidates.append({
                "rank": len(candidates) + 1,
                "worker_id": w_id,
                "name": w_info["name"],
                "distance": d,
                "confidence_score": conf,
                "department": w_info.get("metadata", {}).get("department", "N/A"),
            })
            if len(candidates) >= top_k:
                break

        rank_1 = candidates[0]
        identified = rank_1["distance"] <= threshold

        return {
            "identified": identified,
            "rank_1_match": rank_1 if identified else None,
            "confidence_score": rank_1["confidence_score"] if identified else 0.0,
            "top_k_candidates": candidates,
            "threshold_used": threshold,
        }

    def _get_all_gallery_embeddings(self) -> Tuple[np.ndarray, List[str]]:
        """Collects all embeddings and their corresponding worker IDs."""
        embs = []
        ids = []
        for w_id, w_info in self.workers.items():
            for sess in w_info["sessions"]:
                embs.append(sess["embedding"])
                ids.append(w_id)
        if not embs:
            return np.zeros((0, 128), dtype=np.float32), []
        return np.array(embs, dtype=np.float32), ids

    def list_workers(self) -> List[Dict[str, Any]]:
        """Returns summary list of all enrolled workers."""
        summary = []
        for w_id, w in self.workers.items():
            summary.append({
                "worker_id": w_id,
                "name": w["name"],
                "total_sessions": len(w["sessions"]),
                "created_at": w["created_at"],
                "enrolled_fingers": [s["finger_label"] for s in w["sessions"]],
            })
        return summary

    def save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.workers, f, indent=2)

    def load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    self.workers = json.load(f)
            except Exception:
                self.workers = {}
