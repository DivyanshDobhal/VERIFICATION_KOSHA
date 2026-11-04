#!/usr/bin/env python3
"""
KOSHA LABS – Fingerprint ML Microservice Runner
Starts the FastAPI biometric microservice wrapping your existing trained model
located at /Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION.

Usage:
    python backend/run_ml_service.py [--port 8000] [--host 0.0.0.0] [--model-dir PATH]
"""

import os
import sys
import argparse
import uvicorn

DEFAULT_MODEL_DIR = "/Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION"

def main():
    parser = argparse.ArgumentParser(description="Kosha Labs Fingerprint Model Service Runner")
    parser.add_argument("--port", type=int, default=8000, help="Port to run FastAPI on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    parser.add_argument("--model-dir", type=str, default=DEFAULT_MODEL_DIR, help="Path to your existing model project")
    parser.add_argument("--reload", action="store_true", help="Enable live auto-reload for development")

    args = parser.parse_args()

    os.environ["KOSHA_MODEL_DIR"] = args.model_dir
    if not os.environ.get("MODEL_PATH"):
        os.environ["MODEL_PATH"] = args.model_dir

    print("=" * 70)
    print("  KOSHA LABS – FINGERPRINT RECOGNITION ML SERVICE")
    print("=" * 70)
    print(f"  Target Model Directory: {args.model_dir}")
    print(f"  FastAPI Server URL:    http://{args.host}:{args.port}")
    print(f"  Swagger API Docs:      http://{args.host}:{args.port}/docs")
    print(f"  Health Check:          http://{args.host}:{args.port}/health")
    print("=" * 70)

    # Add backend directory to sys.path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    try:
        from app.ml.model_loader import model_manager
        if model_manager.is_configured():
            print(f"  [✓] Model successfully loaded from: {model_manager.resolved_model_file}")
            print(f"  [✓] Embedding dimension: {model_manager.embedding_dimension}D")
            print(f"  [✓] Expected input tensor: {model_manager.input_shape}")
        else:
            print(f"  [!] Note: Model weights not found directly at {args.model_dir}.")
            print("      Service will run in deterministic feature-extractor mode until weights are mounted.")
    except Exception as e:
        print(f"  [!] Loader inspection warning: {e}")

    print("=" * 70)
    print("Starting Uvicorn server...")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
