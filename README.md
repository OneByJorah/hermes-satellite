<!-- j1-brand:v2 -->
<div align="center">

# Hermes Satellite

A self-hosted, Jarvis-style wake-word voice pipeline that bridges edge audio devices to your Hermes agent over Tailscale — no Home Assistant, no cloud STT/TTS.

[![GitHub](https://img.shields.io/badge/github-OneByJorah%2Fhermes--satellite-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah/hermes-satellite)
[![License](https://img.shields.io/badge/license-MIT-FFB300?style=for-the-badge&labelColor=0d0d0c)](LICENSE)
[![Language](https://img.shields.io/badge/Python-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://python.org)
[![Built by](https://img.shields.io/badge/built%20by-JorahOne%20LLC-FFB300?style=for-the-badge&labelColor=0d0d0c)](https://github.com/OneByJorah)

</div>

---

## Why This Exists

Voice assistants today either lock you into a cloud ecosystem (Alexa, Google Home) or require complex Home Automation hubs. Hermes Satellite gives you a privacy-first alternative: wake-word detection happens on a Raspberry Pi at the edge, audio is only transmitted after the wake word fires, and everything — STT, LLM inference, TTS — routes over Tailscale to your own Hermes hub. No data leaves your network.

## Key Features

| Feature | Why It Matters |
|---|---|
| Edge-based wake-word detection (openWakeWord) | Audio never leaves the satellite until you speak the wake word |
| Faster-Whisper for local STT | Runs on CPU with int8 quantization — no GPU required |
| Piper TTS | Lightweight, offline text-to-speech |
| Hermes VPS integration | Plugs into your existing LLM backend for natural conversation |
| Multi-satellite support | Each satellite gets a unique ID; Honcho maintains separate conversation threads per device |
| Tailscaled networking | Zero-config mesh VPN — no open ports, no reverse proxies |

## Quick Start

```bash
git clone https://github.com/OneByJorah/hermes-satellite.git
cd hermes-satellite

# Hub deployment
cp .env.example .env   # configure HUB_API_KEY, HERMES_VPS_URL, etc.
docker compose up -d

# Satellite deployment (on each Pi)
cp satellite/.env.example satellite/.env   # set unique SATELLITE_ID
docker compose -f satellite/docker-compose.yml up -d
```

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌────────────┐
│  Satellite    │────▶│  Hub (docker)    │────▶│  Hermes    │
│  (Raspberry Pi)│    │  faster-whisper  │     │  VPS (LLM) │
│  openWakeWord │     │  piper TTS       │     │            │
│  VAD + mic    │     │  Honcho memory    │     │            │
└──────────────┘     └──────────────────┘     └────────────┘
         ▲                                          │
         │              ◀───────────────────────────┘
         │                 TTS audio response
         │
  Tailscale mesh VPN (all traffic)
```

## Documentation

| Doc | Description |
|---|---|
| [Hub Setup](docs/hub.md) | Deploy and configure the central processing hub |
| [Satellite Setup](docs/satellite.md) | Flash and configure a Raspberry Pi satellite |
| [Configuration](docs/env.md) | Full `.env` reference for all services |

---

## License

MIT © JorahOne, LLC — see [LICENSE](LICENSE)

<sub>Part of the JorahOne infrastructure ecosystem.</sub>
