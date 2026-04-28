# ─────────────────────────────────────────────────────────────
# EvoAgentX Medical AI — Multi-stage Dockerfile
# ─────────────────────────────────────────────────────────────
# Usage:
#   docker build -t evoagentx .
#   docker run -p 8000:8000 -e OPENAI_API_KEY=xxx evoagentx
#   docker-compose up -d
# ─────────────────────────────────────────────────────────────

FROM python:3.12-slim AS base

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Stage 1: Dependencies ──
FROM base AS deps
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    uvicorn[standard] python-dotenv

# ── Stage 2: Application ──
FROM deps AS app
COPY . .
RUN pip install --no-cache-dir -e ".[tools]"

# Create output directory
RUN mkdir -p /app/output /app/data

# Non-root user
RUN useradd -m -s /bin/bash evoagentx && \
    chown -R evoagentx:evoagentx /app
USER evoagentx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default: API server
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "evoagentx.app.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 3: With CLI ──
FROM app AS full
USER root
RUN pip install --no-cache-dir pytest pytest-cov
USER evoagentx
ENTRYPOINT ["python", "evoagentx/cli.py"]
CMD ["status"]
