FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libasound2-dev portaudio19-dev alsa-utils gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wake.py .

CMD ["python", "wake.py"]
