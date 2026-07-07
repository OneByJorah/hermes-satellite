# =============================================================================
# Hermes Satellite — Wake-word voice pipeline
# JorahOne
# =============================================================================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libasound2-dev portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY satellite/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libasound2 portaudio19-dev alsa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY satellite/ /app/satellite/
COPY hub/ears/ /app/hub/ears/

# Install hub/ears deps (FastAPI bridge)
RUN pip install --no-cache-dir -r /app/hub/ears/requirements.txt

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)" || exit 1

CMD ["python3", "satellite/wake.py"]
