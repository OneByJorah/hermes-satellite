# AGENT_LOG — VoiceSat

## Phase 0 — Intake
- Stack: Python voice AI hub-and-satellite pipeline (ears STT → brain LLM → mouth TTS). Hub (FastAPI bridge + whisper ears + piper mouth) + Satellite (wake-word detection).
- README honest: "CLI/backend-only tool. No screenshots available." Clone URL + author in README.
- Heavy deps: faster-whisper, piper, openwakeword, webrtcvad, sounddevice, numpy. Requires audio hardware (mic) and GPU for real use.

## Phase 1–6
- **Cannot run** in this headless sandbox: needs microphone, speakers, and GPU for real STT/TTS inference. README correctly states no screenshots. This is by design, not a defect.
- `python3 -m compileall hub/ satellite/` → no syntax errors. No fake screenshots or capture scripts present.
- Docker Compose + Dockerfiles already coherent.

## Status: DONE (no issues found; hardware-dependent app correctly documented as backend-only/no-screenshots)