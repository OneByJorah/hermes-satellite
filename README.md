# hermes-satellite

Self-hosted, Jarvis-style wake-word voice pipeline that bridges to your existing
Hermes agent (VPS). No Home Assistant, no cloud STT/TTS — everything runs over
Tailscale.

## Architecture

```
Pi satellite(s)                         Hub (homelab box)
┌────────────────┐  wav (post-wake)   ┌──────────────────────────────┐
│ hermes-wake     │ ─────────────────▶│ hermes-voice-bridge (:8000)  │
│ openWakeWord    │                    │   ├─▶ hermes-ears  (:9000)  │  faster-whisper STT
│ + VAD + mic     │◀───────────────── │   ├─▶ Hermes VPS (your LLM)  │
│ + speaker       │   wav (reply)      │   └─▶ hermes-mouth (:9001)  │  piper TTS
└────────────────┘                    └──────────────────────────────┘
```

Wake-word detection happens locally on each Pi (openWakeWord is light enough
for a Pi 4/5), so nothing streams anywhere until the wake word actually
fires. Only the post-wake utterance and the spoken reply cross the network,
both over your Tailscale mesh.

## 1. Deploy the hub

On your homelab box (alongside `jorahone-ai-stack`):

```bash
cd hermes-satellite
cp .env.example .env
# edit .env: set HERMES_API_URL to your VPS's OpenAI-compatible endpoint
# (LiteLLM router URL) and HERMES_API_KEY

docker compose -f docker-compose.hub.yml up -d --build
```

Then pull the models the containers expect:

- **Whisper**: downloads automatically on first request into the
  `whisper-models` volume — no action needed.
- **Piper voice**: download the `.onnx` + `.onnx.json` pair for
  `en_US-lessac-medium` (or your preferred voice) from the
  [piper voices repo](https://github.com/rhasspy/piper/blob/master/VOICES.md)
  and drop both files into the `piper-voices` volume
  (`docker cp` or mount a host folder instead of the named volume).

Verify:

```bash
curl http://localhost:8000/health
```

## 2. Deploy each Pi satellite

Copy the `satellite/` folder and `docker-compose.satellite.yml` to each Pi.

```bash
cp .env.example .env
# edit .env: set BRIDGE_URL to the hub's Tailscale hostname,
# SATELLITE_ID to something unique per room, WAKE_MODEL to your chosen word

docker compose -f docker-compose.satellite.yml up -d --build
```

Grab a wake-word model: openWakeWord ships pretrained models (`hey_jarvis`,
`alexa`, `hey_mycroft`, etc.) from
[dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) — the
`Model()` call downloads them automatically on first run. To train a fully
custom wake word later, the repo includes a training notebook.

## 3. Talk to it

Say the wake word near any Pi → it VADs the end of your utterance → sends
audio to the hub → hub transcribes, asks your Hermes VPS, synthesizes the
reply → satellite plays it back.

## Memory (Honcho)

The bridge now talks to a self-hosted Honcho instance on your other VM
instead of sending stateless single-turn requests.

- Set `HONCHO_URL` in `.env` to that VM's Tailscale hostname (e.g.
  `http://honcho-vm.tailnet.ts.net:8000`). Leave `HONCHO_API_KEY` blank if
  your self-hosted instance doesn't require auth.
- One user peer (`HONCHO_USER_ID`, defaults to `jhonattan`) represents you
  everywhere. Each satellite's `SATELLITE_ID` becomes its own Honcho
  **session** — so different rooms/sites keep separate conversation
  threads — but Honcho's peer representation for you is workspace-wide, so
  what it learns in one room informs replies in another.
- Every turn: the bridge logs your utterance to the session, pulls
  `session.context(tokens=...)` as prompt-ready messages, sends that to your
  Hermes VPS, then logs the reply back to the session so Honcho's deriver
  can reason over it in the background.
- Tune `HONCHO_CONTEXT_TOKENS` if replies start feeling like they're missing
  earlier context or costing too many tokens per turn.

No changes needed on the Honcho VM side beyond having it reachable at that
Tailscale hostname with its API port exposed on the tailnet.

## Notes / next steps

- GPU: faster-whisper defaults to CPU/int8 so it doesn't fight `llama-server`
  for your 3060's VRAM. Bump `WHISPER_DEVICE=cuda` in `.env` if you want it
  on GPU instead.
- For multiple Pis, just repeat step 2 with a different `SATELLITE_ID` per
  room — they all share the same hub.
