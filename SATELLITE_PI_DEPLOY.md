# Hermes Satellite — Raspberry Pi Deployment

The satellite is a **wake-word + capture client** that runs on a Pi (or any Linux
box with a mic). It is intentionally *not* run on the hub server — it needs real
audio hardware. This guide prepares the image so it is ready the moment you have a Pi.

## Prerequisites (on the Pi)
- Raspberry Pi OS (64-bit) — `uname -m` must show `aarch64`
- Docker + compose plugin installed
- Audio: USB mic or Pi HAT (e.g. seeed-respeaker). Test with `arecord -l`
- The Pi must be on the **same Tailscale network** as the hub (`100.66.142.21`)

## Steps
1. Copy this repo onto the Pi:
   ```bash
   git clone <your-repo> hermes-satellite && cd hermes-satellite
   ```
2. Create the env file:
   ```bash
   cp .env.satellite.example .env
   # edit .env: BRIDGE_URL should point at the hub Tailscale IP :18000
   ```
3. Build for ARM (the Dockerfile is `python:3.11-slim`, multi-arch safe):
   ```bash
   docker compose -f docker-compose.satellite.yml build
   # or cross-build from x86:
   # docker buildx build --platform linux/arm64 -f satellite/Dockerfile -t hermes-wake satellite/
   ```
4. Launch:
   ```bash
   docker compose -f docker-compose.satellite.yml up -d
   ```
   `network_mode: host` + `/dev/snd` give ALSA direct hardware access.

## Verify
- `docker logs hermes-wake` should show the wake model loading (`hey_jarvis`).
- Say the wake word, then speak. The hub (`100.66.142.21:18000/satellite/utterance`)
  should log a `200 OK` and reply with TTS audio pulled back to the Pi.

## Notes
- `WAKE_MODEL` defaults to `hey_jarvis`; swap for any openwakeword model you drop
  into `satellite/`.
- `SATELLITE_ID` namespaces the session in Honcho memory per device.
- No API keys needed — the Pi only talks to the local hub over Tailscale.
