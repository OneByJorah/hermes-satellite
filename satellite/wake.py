import io
import os
import wave

import httpx
import numpy as np
import sounddevice as sd
import webrtcvad
from openwakeword.model import Model

BRIDGE_URL = os.getenv("BRIDGE_URL", "http://hub.tailnet.ts.net:8000")
WAKE_MODEL = os.getenv("WAKE_MODEL", "hey_jarvis")
SATELLITE_ID = os.getenv("SATELLITE_ID", "satellite-1")
WAKE_THRESHOLD = float(os.getenv("WAKE_THRESHOLD", "0.5"))

SAMPLE_RATE = 16000
FRAME_MS = 80  # openWakeWord expects ~80ms chunks at 16kHz
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)
VAD_SILENCE_MS = 900

oww = Model(wakeword_models=[WAKE_MODEL])
vad = webrtcvad.Vad(2)


def record_utterance(stream) -> np.ndarray:
    """Capture audio until ~900ms of silence follows detected speech."""
    frames = []
    silence_ms = 0
    speaking = False

    while True:
        chunk, _ = stream.read(FRAME_SAMPLES)
        pcm = chunk.tobytes()
        frames.append(chunk)

        is_speech = vad.is_speech(pcm, SAMPLE_RATE)
        if is_speech:
            speaking = True
            silence_ms = 0
        elif speaking:
            silence_ms += FRAME_MS
            if silence_ms >= VAD_SILENCE_MS:
                break

    return np.concatenate(frames)


def to_wav_bytes(audio: np.ndarray) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return buf.getvalue()


def play_wav_bytes(data: bytes) -> None:
    with wave.open(io.BytesIO(data), "rb") as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        sd.play(audio, samplerate=wf.getframerate())
        sd.wait()


def send_to_hub(audio: np.ndarray) -> None:
    wav_bytes = to_wav_bytes(audio)
    resp = httpx.post(
        f"{BRIDGE_URL}/satellite/utterance",
        params={"satellite_id": SATELLITE_ID},
        files={"file": ("utterance.wav", wav_bytes, "audio/wav")},
        timeout=60,
    )
    if resp.status_code == 200:
        play_wav_bytes(resp.content)


def main() -> None:
    print(f"[{SATELLITE_ID}] listening for wake word '{WAKE_MODEL}'...")
    with sd.InputStream(
        channels=1, samplerate=SAMPLE_RATE, dtype="int16", blocksize=FRAME_SAMPLES
    ) as stream:
        while True:
            chunk, _ = stream.read(FRAME_SAMPLES)
            prediction = oww.predict(chunk.flatten())
            score = prediction.get(WAKE_MODEL, 0.0)

            if score > WAKE_THRESHOLD:
                print(f"[{SATELLITE_ID}] wake word detected ({score:.2f}), listening...")
                utterance = record_utterance(stream)
                send_to_hub(utterance)
                oww.reset()
                print(f"[{SATELLITE_ID}] back to listening...")


if __name__ == "__main__":
    main()
