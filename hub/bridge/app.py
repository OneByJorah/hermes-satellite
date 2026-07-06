import os
from functools import lru_cache

import httpx
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from honcho import Honcho

EARS_URL = os.getenv("EARS_URL", "http://hermes-ears:9000")
MOUTH_URL = os.getenv("MOUTH_URL", "http://hermes-mouth:9001")

HERMES_API_URL = os.getenv("HERMES_API_URL")
HERMES_API_KEY = os.getenv("HERMES_API_KEY", "")
HERMES_MODEL = os.getenv("HERMES_MODEL", "hermes-3-llama-3.1-8b")

HONCHO_URL = os.getenv("HONCHO_URL")
HONCHO_API_KEY = os.getenv("HONCHO_API_KEY", "")
HONCHO_WORKSPACE_ID = os.getenv("HONCHO_WORKSPACE_ID", "hermes-satellite")
HONCHO_USER_ID = os.getenv("HONCHO_USER_ID", "jhonattan")
HONCHO_ASSISTANT_ID = os.getenv("HONCHO_ASSISTANT_ID", "hermes")
CONTEXT_TOKENS = int(os.getenv("HONCHO_CONTEXT_TOKENS", "4000"))

SYSTEM_PROMPT = (
    "You are Hermes, a concise voice assistant. Keep replies short and "
    "spoken-friendly. Use what you know about the user naturally, without "
    "narrating that you're recalling anything."
)

app = FastAPI(title="hermes-voice-bridge")

# Lazy Honcho so /health works even when Honcho VM is unreachable.
_honcho = None
user_peer = None
assistant_peer = None
_initialized_sessions: set[str] = set(set())


def _get_honcho() -> Honcho:
    global _honcho, user_peer, assistant_peer
    if _honcho is None:
        _honcho = Honcho(
            workspace_id=HONCHO_WORKSPACE_ID,
            api_key=HONCHO_API_KEY or None,
            base_url=HONCHO_URL,
        )
    if user_peer is None:
        user_peer = _honcho.peer(HONCHO_USER_ID)
    if assistant_peer is None:
        assistant_peer = _honcho.peer(HONCHO_ASSISTANT_ID)
    return _honcho


def get_session(satellite_id: str):
    honcho = _get_honcho()
    session = honcho.session(satellite_id)
    if satellite_id not in _initialized_sessions:
        session.add_peers(
            [
                (user_peer, {"observe_me": True, "observe_others": True}),
                (assistant_peer, {"observe_me": False, "observe_others": True}),
            ]
        )
        _initialized_sessions.add(satellite_id)
    return session


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "honcho": bool(HONCHO_URL)}


@app.post("/satellite/utterance")
async def handle_utterance(satellite_id: str = "default", file: UploadFile = File(...)):
    audio_bytes = await file.read()

    async with httpx.AsyncClient(timeout=60) as client:
        # 1. Speech-to-text
        stt_resp = await client.post(
            f"{EARS_URL}/transcribe",
            files={"file": ("utterance.wav", audio_bytes, "audio/wav")},
        )
        stt_resp.raise_for_status()
        text = stt_resp.json()["text"].strip()

        if not text:
            return Response(status_code=204)

        # 2. Honcho: log the utterance, pull prompt-ready context.
        session = get_session(satellite_id)
        session.add_messages([user_peer.message(text)])

        context = session.context(tokens=CONTEXT_TOKENS)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(context.to_openai(assistant=assistant_peer))

        # 3. Ask your Hermes agent on the VPS (OpenAI-compatible endpoint)
        headers = {"Authorization": f"Bearer {HERMES_API_KEY}"} if HERMES_API_KEY else {}
        chat_resp = await client.post(
            HERMES_API_URL,
            headers=headers,
            json={
                "model": HERMES_MODEL,
                "messages": messages,
                "user": satellite_id,
            },
        )
        chat_resp.raise_for_status()
        reply_text = chat_resp.json()["choices"][0]["message"]["content"]

        # 4. Store the reply so future turns (any room) have it as context
        session.add_messages([assistant_peer.message(reply_text)])

        # 5. Text-to-speech
        tts_resp = await client.post(f"{MOUTH_URL}/synthesize", json={"text": reply_text})
        tts_resp.raise_for_status()

    return Response(content=tts_resp.content, media_type="audio/wav")
