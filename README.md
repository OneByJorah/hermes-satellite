# VoiceSat

Jarvis-style wake-word voice pipeline with Raspberry Pi satellites — local STT, LLM, TTS, and persistent memory.

![status](https://img.shields.io/badge/status-active-FFB300?style=flat-square)
![language](https://img.shields.io/badge/python-3.11+-0d0d0c?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-FFB300?style=flat-square)

## Overview

VoiceSat is a self-hosted, Jarvis-style voice assistant that runs on Raspberry Pi satellites connected to a central hub. Wake-word detection (openWakeWord) runs locally on each Pi — nothing streams until the wake word fires. Audio is then sent to the hub for STT (faster-whisper), LLM inference, and TTS (Piper), with responses played back locally. Persistent memory via Honcho. All traffic over Tailscale — no cloud STT/TTS.

## Features

- Wake-word detection — local openWakeWord on Raspberry Pi, nothing streams until wake word fires
- Real-time pipeline — audio > VAD > STT > LLM > TTS > audio playback
- Privacy-first — everything runs locally over Tailscale, no cloud STT/TTS
- Persistent memory — Honcho integration for conversation context across sessions
- Multi-satellite — deploy multiple Pis as satellites, each with unique room IDs
- Containerized — Docker Compose for both hub and satellite deployment
- Local STT — faster-whisper for speech-to-text (CPU or GPU)
- Local TTS — Piper ONNX for text-to-speech synthesis

## Architecture / Tech Stack

- **Hub**: Python 3.11+, faster-whisper (STT), Piper (TTS), Ollama (LLM), Honcho (memory)
- **Satellite**: Raspberry Pi, openWakeWord, Docker
- **Networking**: Tailscale mesh
- **Deployment**: Docker Compose (hub + satellite)

## Installation

### Hub

```bash
git clone https://github.com/OneByJorah/VoiceSat.git
cd VoiceSat

cp .env.example .env  # Configure LLM, memory, TTS settings
docker compose up -d
```

### Satellite (Raspberry Pi)

```bash
# See SATELLITE_PI_DEPLOY.md for detailed Pi setup
cd satellite
docker compose up -d
```

## Configuration

| Variable | Description |
|----------|-------------|
| `OLLAMA_URL` | Ollama endpoint on hub |
| `HONCHO_API_URL` | Honcho memory API |
| `WHISPER_MODEL` | faster-whisper model size |
| `PIPER_VOICE` | Piper TTS voice |
| `WAKE_WORD_MODEL` | openWakeWord model |

See `.env.example` for full options.

## License

MIT — see [LICENSE](LICENSE).

---
Part of the JorahOne / J1 ecosystem — privacy-first voice AI across Raspberry Pi satellites.
