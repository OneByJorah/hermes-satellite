<div align="center">

![VoiceSat banner](docs/assets/banner.svg)

# VoiceSat

Jarvis-style wake-word voice pipeline

![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Language](https://img.shields.io/badge/language-Python-blue)
</div>

---

<p align="center">
  <img src="docs/assets/screenshot.png" alt="VoiceSat preview" width="90%">
</p>

<br>

---

## Features

- **Wake Word Detection** — "Hey Jarvis" style activation with openWakeWord.
- **Local STT** — Speech-to-text with faster-whisper (no cloud).
- **Local LLM** — Private language model processing.
- **Local TTS** — Text-to-speech with Piper.
- **Persistent Memory** — Long-term conversation memory with Honcho.
- **Raspberry Pi** — Optimized for Raspberry Pi 4/5.
- **100% Private** — All processing stays on-device.
- **Multi-Satellite** — Deploy multiple satellite units.

## Quick Start

### Raspberry Pi

```bash
git clone https://github.com/OneByJorah/VoiceSat.git
cd VoiceSat

pip install -r requirements.txt

# Download models
python3 setup.py download-models

# Run the voice pipeline
python3 voicesat.py
```

### Docker

```bash
docker compose up -d
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WAKE_WORD` | `hey jarvis` | Wake word phrase |
| `STT_MODEL` | `base` | faster-whisper model size |
| `LLM_MODEL` | `llama2` | Local LLM model |
| `TTS_VOICE` | `en_US-lessac-medium` | Piper voice |
| `HONCHO_API_KEY` | — | Honcho API key for memory |
| `HONCHO_PROJECT_ID` | — | Honcho project ID |
| `AUDIO_DEVICE` | `default` | Audio input device |

## Architecture

```
Microphone ──▶ Wake Word ──▶ STT ──▶ LLM ──▶ TTS ──▶ Speaker
    │              │           │        │        │
    │              │           │        │        └──▶ Piper
    │              │           │        └──▶ Local LLM
    │              │           └──▶ faster-whisper
    │              └──▶ openWakeWord
    └──▶ USB Audio
```

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Board** | Raspberry Pi 4 (2GB) | Raspberry Pi 5 (4GB+) |
| **RAM** | 2GB | 4GB+ |
| **Storage** | 16GB SD | 32GB+ SSD |
| **Audio** | USB mic + speaker | ReSpeaker HAT |
| **Network** | WiFi | Ethernet |

## Project Structure

```
VoiceSat/
├── voicesat.py              # Main entry point
├── pipeline/
│   ├── __init__.py
│   ├── wake_word.py         # Wake word detection
│   ├── stt.py               # Speech-to-text
│   ├── llm.py               # Language model
│   ├── tts.py               # Text-to-speech
│   └── memory.py            # Honcho memory
├── config/                  # Configuration files
├── models/                  # Downloaded models (gitignored)
├── docker-compose.yml       # Docker deployment
├── requirements.txt         # Python dependencies
└── README.md
```

## Model Downloads

| Model | Size | Purpose |
|-------|------|---------|
| openWakeWord | ~10MB | Wake word detection |
| faster-whisper (base) | ~150MB | Speech-to-text |
| Piper (lessac) | ~50MB | Text-to-speech |
| Llama2 (7B) | ~4GB | Language model |

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards.

## Security

For security concerns, see [SECURITY.md](SECURITY.md). Please report vulnerabilities to **info@jorahone.com** — do not use public issues.

## License

MIT © Jhonattan L. Jimenez

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## 🔒 Security

Found a vulnerability? Please follow our [Security Policy](SECURITY.md) and report privately to `security@jorahone.com`.

## 📄 License

[MIT License](LICENSE) © Jhonattan L. Jimenez (OneByJorah)

---

<p align="center">Built with 🌴 by <a href="https://github.com/OneByJorah">OneByJorah</a> · <a href="https://jorahone.com">jorahone.com</a></p>
