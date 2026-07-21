<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Tailscale-006AFF?style=for-the-badge&logo=tailscale&logoColor=white">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge">
</div>

<br>

<div align="center">
  <h1>🛰️ VoiceSat</h1>
  <p><strong>Jarvis-Style Wake-Word Voice Pipeline</strong></p>
  <p>Self-hosted voice assistant with Raspberry Pi satellites — wake-word detection, STT, LLM, TTS — all local</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-configuration">Configuration</a> •
    <a href="#-deployment">Deployment</a>
  </p>
</div>

---

## 📸 Screenshot

This is a CLI/backend-only tool. No screenshots available.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎤 **Wake-Word Detection** | Local openWakeWord on Raspberry Pi — nothing streams until wake word fires |
| 🔊 **Real-Time Pipeline** | Audio → VAD → STT → LLM → TTS → Audio playback |
| 🏠 **Privacy-First** | Everything runs locally over Tailscale — no cloud STT/TTS |
| 🧠 **Persistent Memory** | Honcho integration for conversation context across sessions |
| 🛰️ **Multi-Satellite** | Deploy multiple Pis as satellites, each with unique room IDs |
| 🐳 **Containerized** | Docker Compose for both hub and satellite deployment |
| 🎯 **Local STT** | faster-whisper for speech-to-text (CPU or GPU) |
| 🗣️ **Local TTS** | Piper ONNX for text-to-speech synthesis |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VoiceSat Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Pi Satellite(s)                    Hub (Homelab Box)          │
│  ┌────────────────┐  wav (post-wake) ┌──────────────────────┐  │
│  │ hermes-wake    │ ────────────────▶│ hermes-voice-bridge  │  │
│  │ openWakeWord   │                  │      (:8000)         │  │
│  │ + VAD + mic    │◀────────────────│  ├─▶ hermes-ears     │  │
│  │ + speaker      │  wav (reply)     │  │   (:9000)         │  │
│  └────────────────┘                  │  ├─▶ Hermes VPS      │  │
│                                      │  │   (your LLM)      │  │
│                                      │  └─▶ hermes-mouth   │  │
│                                      │      (:9001)         │  │
│                                      └──────────────────────┘  │
│                                                                 │
│  Tailscale Mesh — All services communicate securely             │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow

```
Wake Word Detected → VAD Ends Utterance → Audio Sent to Hub → 
STT Transcription → LLM Response → TTS Synthesis → Audio Playback
```

---

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi 4/5 (satellite)
- Homelab server (hub)
- Docker & Docker Compose v2
- Tailscale (for secure networking)
- Microphone + speaker (for satellite)

### 1. Deploy the Hub

On your homelab box:

```bash
git clone https://github.com/OneByJorah/VoiceSat.git
cd VoiceSat
cp .env.example .env
# Edit .env: set HERMES_API_URL and HERMES_API_KEY

docker compose -f docker-compose.hub.yml up -d --build
```

### 2. Download Piper Voice

```bash
# Download voice model (en_US-lessac-medium or your preferred voice)
# From: https://github.com/rhasspy/piper/blob/master/VOICES.md
# Place .onnx + .onnx.json in piper-voices volume
```

### 3. Deploy Satellite to Pi

```bash
# Copy satellite/ folder and docker-compose.satellite.yml to Pi
cp .env.example .env
# Edit .env: set BRIDGE_URL, SATELLITE_ID, WAKE_MODEL

docker compose -f docker-compose.satellite.yml up -d --build
```

### 4. Talk to It

Say the wake word near any Pi → it captures your voice → sends to hub → hub processes and responds → satellite plays back the reply.

---

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

### Hub Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_API_URL` | — | Your Hermes VPS OpenAI-compatible endpoint |
| `HERMES_API_KEY` | — | API key for Hermes VPS |
| `HUB_BIND_IP` | `127.0.0.1` | Interface to bind hub services to (set to your Tailscale/mesh IP to reach satellites) |
| `HONCHO_URL` | — | Honcho instance Tailscale hostname |
| `HONCHO_API_KEY` | — | Honcho API key (blank if no auth) |
| `HONCHO_USER_ID` | `appuser` | User peer ID for Honcho |
| `HONCHO_CONTEXT_TOKENS` | `2048` | Context tokens for conversation history |

### Satellite Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BRIDGE_URL` | — | Hub endpoint URL (e.g., `http://hub.tailnet.ts.net:18000/satellite/utterance`) |
| `SATELLITE_ID` | `living-room` | Unique ID per satellite/room |
| `WAKE_MODEL` | `hey_jarvis` | Wake-word model name |

### Speech Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `small.en` | STT model size: `base.en`, `small.en`, `medium.en` |
| `WHISPER_DEVICE` | `cpu` | `cpu` or `cuda` (GPU acceleration) |
| `PIPER_VOICE` | — | Path to Piper ONNX voice file |

---

## 📡 Services

| Service | Port | Description |
|---------|------|-------------|
| **hermes-voice-bridge** | 8000 | Main bridge orchestrator |
| **hermes-ears** | 9000 | faster-whisper STT service |
| **hermes-mouth** | 9001 | Piper TTS service |

---

## 🧠 Memory (Honcho)

VoiceSat integrates with self-hosted Honcho for persistent conversation memory:

- **Session-Based**: Each satellite gets its own Honcho session
- **Workspace-Wide Learning**: What the assistant learns in one room informs replies in another
- **Context Continuity**: Conversation history persists across sessions
- **Tunable Context**: Adjust `HONCHO_CONTEXT_TOKENS` for response quality vs. cost

### Honcho Setup

1. Deploy Honcho on a separate VM (or use from AIStack/StackForge)
2. Set `HONCHO_URL` to the Tailscale hostname
3. Leave `HONCHO_API_KEY` blank if your instance doesn't require auth

---

## 🐳 Deployment

### Hub (Homelab)

```bash
# With Honcho memory
docker compose -f docker-compose.hub.yml up -d --build

# Verify
curl http://localhost:8000/health
```

### Satellite (Raspberry Pi)

```bash
# Deploy to each Pi
docker compose -f docker-compose.satellite.yml up -d --build
```

### Multi-Satellite

Deploy multiple satellites with different `SATELLITE_ID` values:

| Satellite | Room | SATELLITE_ID |
|-----------|------|--------------|
| Pi 1 | Living Room | `living-room` |
| Pi 2 | Office | `office` |
| Pi 3 | Kitchen | `kitchen` |

All satellites share the same hub and Honcho memory.

---

## 📁 Project Structure

```
VoiceSat/
├── hub/                           # Hub components
│   ├── voice_bridge.py            # Main bridge orchestrator
│   ├── hermes_ears.py             # STT service (faster-whisper)
│   └── hermes_mouth.py            # TTS service (Piper)
├── satellite/                     # Pi satellite code
│   ├── hermes_wake.py             # Wake-word detection (openWakeWord)
│   └── audio_capture.py           # Microphone/speaker handling
├── docker-compose.hub.yml         # Hub deployment
├── docker-compose.satellite.yml   # Satellite deployment
├── .env.example                   # Configuration template
├── SATELLITE_PI_DEPLOY.md         # Pi deployment guide
└── README.md
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/wake` | POST | Wake-word triggered (satellite → hub) |
| `/audio` | POST | Send audio for processing |
| `/status` | GET | System status |

---

## 🛠️ Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No response after wake word | Hub not reachable | Check `BRIDGE_URL` and Tailscale connectivity |
| Poor transcription quality | Wrong Whisper model | Try `medium.en` or enable GPU with `WHISPER_DEVICE=cuda` |
| TTS audio sounds robotic | Wrong voice model | Download a different Piper voice from [VOICES.md](https://github.com/rhasspy/piper/blob/master/VOICES.md) |
| Memory not persisting | Honcho not configured | Set `HONCHO_URL` and verify Honcho is running |
| High latency | CPU bottleneck | Enable GPU for STT: `WHISPER_DEVICE=cuda` |

---

## 🗺️ Roadmap

- [x] Wake-word detection with openWakeWord
- [x] faster-whisper STT integration
- [x] Piper TTS synthesis
- [x] Honcho memory integration
- [ ] Barge-in support (interrupt mid-response)
- [ ] Multi-language support
- [ ] Custom wake-word training
- [ ] WebRTC transport for browser-based calling
- [ ] Voice cloning support

---

## 📄 License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>🛰️ Your Jarvis, self-hosted and private</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
