import os
import subprocess
import tempfile

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

VOICE = os.getenv("PIPER_VOICE", "en_US-lessac-medium")
VOICES_DIR = "/voices"
PIPER_BIN = "/app/piper/piper"

app = FastAPI(title="hermes-mouth")


class SpeakRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "voice": VOICE}


@app.post("/synthesize")
def synthesize(req: SpeakRequest):
    model_path = os.path.join(VOICES_DIR, f"{VOICE}.onnx")
    out_path = tempfile.mktemp(suffix=".wav")

    subprocess.run(
        [PIPER_BIN, "--model", model_path, "--output_file", out_path],
        input=req.text.encode("utf-8"),
        check=True,
    )

    return FileResponse(out_path, media_type="audio/wav", filename="reply.wav")
