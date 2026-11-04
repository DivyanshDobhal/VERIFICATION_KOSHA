import numpy as np
from typing import List, Tuple, Dict, Any
from app.config import settings

class BiometricMatcher:
    """Computes cosine similarity between 128-dimensional unit normalized embeddings."""

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        dot = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    @classmethod
    def match_one_to_n(
        cls, 
        query_vector: np.ndarray, 
        candidate_records: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]], float]:
        """Performs 1:N biometric gallery search.
        Returns:
            status: 'MATCH' | 'UNCERTAIN' | 'NO_MATCH'
            candidates: Ranked list of matches
            best_score: Highest similarity score
        """
        if not candidate_records:
            return "NO_MATCH", [], 0.0

        scores = []
        for record in candidate_records:
            cand_vec = record["embedding"]
            sim = cls.cosine_similarity(query_vector, cand_vec)
            scores.append({
                "worker_id": record["worker_id"],
                "worker_name": record["worker_name"],
                "department": record["department"],
                "site_name": record.get("site_name", "Assigned Site"),
                "similarity_score": round(sim, 4),
            })

        # Sort descending by similarity
        scores.sort(key=lambda x: x["similarity_score"], reverse=True)
        best_match = scores[0]
        best_score = best_match["similarity_score"]

        # Calibrated thresholds:
        # >= MATCH_CONFIDENCE_THRESHOLD (0.85) -> Confident MATCH
        # between UNCERTAIN_LOW_THRESHOLD (0.60) and 0.85 -> UNCERTAIN (requires supervisor review)
        # < UNCERTAIN_LOW_THRESHOLD -> NO_MATCH
        if best_score >= settings.MATCH_CONFIDENCE_THRESHOLD:
            return "MATCH", scores[:3], best_score
        elif best_score >= settings.UNCERTAIN_LOW_THRESHOLD:
            return "UNCERTAIN", scores[:3], best_score
        else:
            return "NO_MATCH", scores[:3], best_score

matcher = BiometricMatcher()
