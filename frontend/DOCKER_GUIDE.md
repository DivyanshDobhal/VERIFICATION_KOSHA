# KOSHA LABS – Containerization Guide

This guide describes how to build, run, and orchestrate the Kosha Labs application and the Fingerprint ML microservice using Docker.

---

## 1. Quick Start: Multi-Container Setup (`docker-compose`)

This spins up both the **Full-Stack Application** (port 3000) and the **Python FastAPI ML Microservice** (port 8000), mounting your local trained model folder automatically.

```bash
# 1. Run both containers
docker compose up --build

# 2. Or run detached in the background
docker compose up -d --build
```

### Accessing the Services
- **Web / Mobile Application**: [http://localhost:3000](http://localhost:3000)
- **FastAPI ML Service**: [http://localhost:8000](http://localhost:8000)
- **Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ML Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 2. Mounting Your Trained Model

The `docker-compose.yml` mounts your local folder directly into the ML container:

```yaml
volumes:
  - /Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION:/models:ro
```

If your model is stored in a different path, you can set the `KOSHA_MODEL_DIR` environment variable before starting:

```bash
export KOSHA_MODEL_DIR="/path/to/your/model"
docker compose up --build
```

---

## 3. Building Single Containers Individually

### A. Full-Stack Web App (`Dockerfile`)
```bash
# Build the production image
docker build -t kosha-labs-app .

# Run the container
docker run -p 3000:3000 \
  -e ML_SERVICE_URL="http://host.docker.internal:8000" \
  kosha-labs-app
```

### B. Python ML Microservice (`backend/Dockerfile`)
```bash
# Build the ML image
docker build -t kosha-ml-service -f backend/Dockerfile backend

# Run the container with your model mounted
docker run -p 8000:8000 \
  -v /Users/divyanshdobhal/Desktop/PROJECTS/KOSHA_VERIFICATION:/models:ro \
  kosha-ml-service
```

---

## 4. Useful Docker Commands

```bash
# View running containers
docker ps

# Follow container logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild without cache
docker compose build --no-cache
```
