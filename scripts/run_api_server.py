"""
Uvicorn launcher script for KOSHA LABS Biometric Fingerprint REST API.
"""

import sys
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    print("=" * 60)
    print("Launching KOSHA LABS Biometric Fingerprint Recognition Service")
    print("Host: 127.0.0.1, Port: 8000, Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("src.service.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()

