"""
Dataset loader and filename parser for SOCOFing.
Extracts subject IDs, finger identifiers, alteration types, and source fingerprint group identifiers.
"""

from pathlib import Path
import re
from typing import Dict, Any, List, Optional
import pandas as pd

FILENAME_REGEX = re.compile(
    r"^(\d+)__([MF])_([A-Za-z]+)_([A-Za-z]+)_finger(?:_([A-Za-z0-9]+))?\.BMP$",
    re.IGNORECASE,
)

ALTERATION_MAP = {
    "cr": "Central Rotation",
    "obl": "Obliteration",
    "zcut": "Z-cut",
}


def parse_filename(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Parses a single SOCOFing filename into structured metadata.
    
    Returns:
        dict with fields:
            - subject_id (int): 1 to 600
            - gender (str): 'M' or 'F'
            - hand (str): 'Left' or 'Right'
            - finger (str): 'thumb', 'index', 'middle', 'ring', 'little'
            - finger_label (str): e.g. 'Right_index_finger'
            - source_finger_group (str): e.g. '100_Right_index_finger' (CRITICAL for zero leakage)
            - is_altered (bool): True if altered, False if Real/Original
            - alteration_code (str): 'CR', 'Obl', 'Zcut' or 'None'
            - alteration_category (str): 'Central Rotation', 'Obliteration', 'Z-cut' or 'Original'
            - difficulty (str): 'Easy', 'Medium', 'Hard' or 'Original'
            - file_path (str): absolute path as string
    """
    path = Path(filepath)
    filename = path.name
    match = FILENAME_REGEX.match(filename)
    if not match:
        return None

    subject_id = int(match.group(1))
    gender = match.group(2).upper()
    hand = match.group(3).capitalize()
    finger = match.group(4).lower()
    alt_code = match.group(5)

    finger_label = f"{hand}_{finger}_finger"
    source_finger_group = f"{subject_id}_{finger_label}"

    parent_name = path.parent.name
    if "Easy" in parent_name:
        difficulty = "Easy"
    elif "Medium" in parent_name:
        difficulty = "Medium"
    elif "Hard" in parent_name:
        difficulty = "Hard"
    elif "Real" in parent_name:
        difficulty = "Original"
    else:
        difficulty = "Unknown"

    if alt_code:
        alt_code_clean = alt_code.lower()
        alt_category = ALTERATION_MAP.get(alt_code_clean, alt_code)
        is_altered = True
    else:
        alt_code = "None"
        alt_category = "Original"
        is_altered = False
        difficulty = "Original"

    return {
        "filename": filename,
        "file_path": str(path.resolve()),
        "subject_id": subject_id,
        "gender": gender,
        "hand": hand,
        "finger": finger,
        "finger_label": finger_label,
        "source_finger_group": source_finger_group,
        "is_altered": is_altered,
        "alteration_code": alt_code,
        "alteration_category": alt_category,
        "difficulty": difficulty,
    }


def scan_socofing_dataset(dataset_root: Path) -> pd.DataFrame:
    """
    Scans the SOCOFing directory, parses all images, and returns a DataFrame.
    Gracefully prevents duplicate entries if a nested directory exists.
    """
    root = Path(dataset_root)
    records: List[Dict[str, Any]] = []
    seen_paths = set()

    # Search for Real and Altered subdirectories
    search_dirs = []
    real_dir = root / "Real"
    altered_dir = root / "Altered"

    if real_dir.exists():
        search_dirs.append(real_dir)
    if altered_dir.exists():
        search_dirs.append(altered_dir)

    # Fallback to scanning root if standard subdirs not found directly
    if not search_dirs:
        search_dirs = [root]

    for sdir in search_dirs:
        for file_path in sdir.rglob("*.BMP"):
            # Avoid redundant nested 'SOCOFing/SOCOFing' if present
            resolved = str(file_path.resolve())
            if "/SOCOFing/SOCOFing/" in resolved:
                continue
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)

            meta = parse_filename(file_path)
            if meta:
                records.append(meta)

    df = pd.DataFrame(records)
    return df

