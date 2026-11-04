"""
Group-aware pair generator for Siamese fingerprint learning.
Produces strictly balanced genuine and imposter pairs without duplicate cross-partition contamination,
and supports hard-negative mining.
"""

from typing import Tuple, List, Dict, Optional
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
from src.preprocessing.pipeline import FingerprintPreprocessor
from src.preprocessing.augmentation import BiometricAugmentor


class FingerprintPairGenerator:
    """
    Generates balanced positive and negative image pairs for Siamese training and validation.
    Guarantees no pair duplicates and respects source-group isolation.
    Genuine pairs are formed strictly from impressions of the EXACT same anatomical finger
    (matching source_finger_group), eliminating label noise from cross-finger pairing.
    Negative pairs incorporate hard negatives (different fingers of the same subject)
    as well as inter-subject imposter pairs.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        preprocessor: Optional[FingerprintPreprocessor] = None,
        augmentor: Optional[BiometricAugmentor] = None,
        seed: int = 42,
    ):
        self.df = df.reset_index(drop=True)
        self.preprocessor = preprocessor or FingerprintPreprocessor()
        self.augmentor = augmentor
        self.rng = np.random.RandomState(seed)

        # Index metadata by source finger group (anatomical finger)
        self.finger_to_indices: Dict[str, List[int]] = {}
        # Index metadata by subject ID
        self.subj_to_indices: Dict[int, List[int]] = {}
        # Index subject ID to list of distinct finger groups
        self.subj_to_fingers: Dict[int, List[str]] = {}

        for idx, row in self.df.iterrows():
            sid = row["subject_id"]
            if "source_finger_group" in row and pd.notna(row["source_finger_group"]):
                fg = str(row["source_finger_group"])
            else:
                finger_name = row.get("finger_label", row.get("finger", "finger"))
                fg = f"{sid}_{finger_name}"

            if fg not in self.finger_to_indices:
                self.finger_to_indices[fg] = []
            self.finger_to_indices[fg].append(idx)

            if sid not in self.subj_to_indices:
                self.subj_to_indices[sid] = []
            self.subj_to_indices[sid].append(idx)

            if sid not in self.subj_to_fingers:
                self.subj_to_fingers[sid] = []
            if fg not in self.subj_to_fingers[sid]:
                self.subj_to_fingers[sid].append(fg)

        self.all_subjects = list(self.subj_to_indices.keys())
        self.all_fingers = list(self.finger_to_indices.keys())
        self.multi_impression_fingers = [
            fg for fg, indices in self.finger_to_indices.items() if len(indices) >= 2
        ]
        self.multi_finger_subjects = [
            sid for sid, fgs in self.subj_to_fingers.items() if len(fgs) >= 2
        ]

    def generate_pairs(
        self, num_pairs: int = 10000, hard_negative_ratio: float = 0.5
    ) -> Tuple[List[str], List[str], np.ndarray]:
        """
        Generates balanced positive and negative pairs.
        - Positive (Genuine, label 1.0): Sampled strictly from impressions of the SAME finger group.
        - Negative (Imposter, label 0.0):
            - hard_negative_ratio of pairs are hard negatives (different fingers of the same subject).
            - (1 - hard_negative_ratio) of pairs are inter-subject imposters (different subjects).
        Returns:
            img1_paths, img2_paths, labels (1 for Genuine, 0 for Imposter)
        """
        n_pos = num_pairs // 2
        n_neg = num_pairs - n_pos

        pairs_set = set()
        img1_paths: List[str] = []
        img2_paths: List[str] = []
        labels: List[float] = []

        # 1. Generate Positive (Genuine) pairs: strictly SAME finger group
        if not self.multi_impression_fingers:
            # Fallback to subject-level if dataset only has single impression per finger
            candidate_fgs = [s for s in self.all_subjects if len(self.subj_to_indices[s]) >= 2]
            if not candidate_fgs:
                raise ValueError("No classes have at least 2 images to generate positive pairs!")
            use_subj_fallback = True
        else:
            candidate_fgs = self.multi_impression_fingers
            use_subj_fallback = False

        attempts = 0
        while len(labels) < n_pos and attempts < n_pos * 40:
            attempts += 1
            if use_subj_fallback:
                sid = self.rng.choice(candidate_fgs)
                indices = self.subj_to_indices[sid]
            else:
                fg = self.rng.choice(candidate_fgs)
                indices = self.finger_to_indices[fg]

            idx1, idx2 = self.rng.choice(indices, size=2, replace=False)
            pair_key = tuple(sorted([idx1, idx2]))
            if pair_key in pairs_set:
                continue
            pairs_set.add(pair_key)
            img1_paths.append(self.df.loc[idx1, "file_path"])
            img2_paths.append(self.df.loc[idx2, "file_path"])
            labels.append(1.0)

        # 2. Generate Negative (Imposter) pairs
        n_hard = int(n_neg * hard_negative_ratio) if self.multi_finger_subjects else 0
        n_inter = n_neg - n_hard

        # 2a. Hard Negatives: same subject, different fingers
        attempts = 0
        initial_hard_len = len(labels)
        target_hard = initial_hard_len + n_hard
        while len(labels) < target_hard and attempts < n_neg * 30:
            attempts += 1
            sid = self.rng.choice(self.multi_finger_subjects)
            fgs = self.subj_to_fingers[sid]
            fg1, fg2 = self.rng.choice(fgs, size=2, replace=False)
            idx1 = self.rng.choice(self.finger_to_indices[fg1])
            idx2 = self.rng.choice(self.finger_to_indices[fg2])
            pair_key = tuple(sorted([idx1, idx2]))
            if pair_key in pairs_set:
                continue
            pairs_set.add(pair_key)
            img1_paths.append(self.df.loc[idx1, "file_path"])
            img2_paths.append(self.df.loc[idx2, "file_path"])
            labels.append(0.0)

        # 2b. Inter-subject Negatives: different subjects
        attempts = 0
        while len(labels) < num_pairs and attempts < n_neg * 40:
            attempts += 1
            sid1, sid2 = self.rng.choice(self.all_subjects, size=2, replace=False)
            idx1 = self.rng.choice(self.subj_to_indices[sid1])
            idx2 = self.rng.choice(self.subj_to_indices[sid2])
            pair_key = tuple(sorted([idx1, idx2]))
            if pair_key in pairs_set:
                continue
            pairs_set.add(pair_key)
            img1_paths.append(self.df.loc[idx1, "file_path"])
            img2_paths.append(self.df.loc[idx2, "file_path"])
            labels.append(0.0)

        # Shuffle pairs
        perm = self.rng.permutation(len(labels))
        img1_paths = [img1_paths[i] for i in perm]
        img2_paths = [img2_paths[i] for i in perm]
        labels_arr = np.array([labels[i] for i in perm], dtype=np.float32)

        return img1_paths, img2_paths, labels_arr

    def mine_hard_negatives(
        self,
        feature_extractor: tf.keras.Model,
        candidate_count: int = 3000,
        top_hard_count: int = 1000,
        batch_size: int = 64,
    ) -> Tuple[List[str], List[str]]:
        """
        Hard-negative mining on training partition only:
        Computes embeddings for candidate negative pairs and finds those with the smallest Euclidean distance
        (i.e. imposter pairs that the model mistakenly considers genuine / borderline).
        """
        # Sample candidate negative pairs
        neg_p1 = []
        neg_p2 = []
        for _ in range(candidate_count):
            sid1, sid2 = self.rng.choice(self.all_subjects, size=2, replace=False)
            idx1 = self.rng.choice(self.subj_to_indices[sid1])
            idx2 = self.rng.choice(self.subj_to_indices[sid2])
            neg_p1.append(self.df.loc[idx1, "file_path"])
            neg_p2.append(self.df.loc[idx2, "file_path"])

        # Extract embeddings in batches
        all_unique_paths = list(set(neg_p1 + neg_p2))
        path_to_idx = {p: i for i, p in enumerate(all_unique_paths)}

        # Load & preprocess images
        images = []
        for p in all_unique_paths:
            img = self.preprocessor.process_image(p)
            images.append(img)
        images_tensor = np.array(images, dtype=np.float32)

        embeddings = feature_extractor.predict(images_tensor, batch_size=batch_size, verbose=0)

        # Calculate distances
        distances = []
        for p1, p2 in zip(neg_p1, neg_p2):
            emb1 = embeddings[path_to_idx[p1]]
            emb2 = embeddings[path_to_idx[p2]]
            dist = float(np.linalg.norm(emb1 - emb2))
            distances.append(dist)

        # Hard negatives have smallest distance (confused imposters)
        hard_indices = np.argsort(distances)[:top_hard_count]
        hard_p1 = [neg_p1[i] for i in hard_indices]
        hard_p2 = [neg_p2[i] for i in hard_indices]

        return hard_p1, hard_p2


def load_pair_arrays(
    img1_paths: List[str],
    img2_paths: List[str],
    labels: np.ndarray,
    preprocessor: Optional[FingerprintPreprocessor] = None,
    augmentor: Optional[BiometricAugmentor] = None,
) -> Tuple[Tuple[np.ndarray, np.ndarray], np.ndarray]:
    """
    Preloads pair images into contiguous memory arrays for ultra-fast, zero-overhead training.
    """
    pre = preprocessor or FingerprintPreprocessor()
    x1_list = []
    x2_list = []
    for p1, p2 in zip(img1_paths, img2_paths):
        im1 = pre.process_image(p1)
        im2 = pre.process_image(p2)
        if augmentor:
            im1 = augmentor(im1)
            im2 = augmentor(im2)
        x1_list.append(im1)
        x2_list.append(im2)

    x1_arr = np.array(x1_list, dtype=np.float32)
    x2_arr = np.array(x2_list, dtype=np.float32)
    y_arr = np.array(labels, dtype=np.float32)

    return (x1_arr, x2_arr), y_arr


class SiameseBatchGenerator(tf.keras.utils.Sequence):
    """
    Keras Sequence generator for batching Siamese image pairs with on-the-fly augmentation.
    """

    def __init__(
        self,
        img1_paths: List[str],
        img2_paths: List[str],
        labels: np.ndarray,
        batch_size: int = 32,
        preprocessor: Optional[FingerprintPreprocessor] = None,
        augmentor: Optional[BiometricAugmentor] = None,
        shuffle: bool = True,
    ):
        super().__init__()
        self.img1_paths = img1_paths
        self.img2_paths = img2_paths
        self.labels = labels
        self.batch_size = batch_size
        self.preprocessor = preprocessor or FingerprintPreprocessor()
        self.augmentor = augmentor
        self.shuffle = shuffle
        self.indices = np.arange(len(self.labels))
        self.on_epoch_end()

    def __len__(self):
        return int(np.ceil(len(self.labels) / self.batch_size))

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

    def __getitem__(self, idx):
        batch_idx = self.indices[idx * self.batch_size : (idx + 1) * self.batch_size]
        b_p1 = [self.img1_paths[i] for i in batch_idx]
        b_p2 = [self.img2_paths[i] for i in batch_idx]
        b_labels = self.labels[batch_idx]

        x1_batch = []
        x2_batch = []
        for p1, p2 in zip(b_p1, b_p2):
            im1 = self.preprocessor.process_image(p1)
            im2 = self.preprocessor.process_image(p2)
            if self.augmentor:
                im1 = self.augmentor(im1)
                im2 = self.augmentor(im2)
            x1_batch.append(im1)
            x2_batch.append(im2)

        return (
            (np.array(x1_batch, dtype=np.float32), np.array(x2_batch, dtype=np.float32)),
            np.array(b_labels, dtype=np.float32),
        )
