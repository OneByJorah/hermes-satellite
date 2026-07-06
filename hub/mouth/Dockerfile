FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends wget tar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pull the piper binary release
RUN wget -qO- https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz | tar xz -C /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 9001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9001"]
