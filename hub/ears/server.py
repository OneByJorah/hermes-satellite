import os
import tempfile

from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel

MODEL_NAME = os.getenv("WHISPER_MODEL", "small.en")
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

app = FastAPI(title="hermes-ears")
model = WhisperModel(
    MODEL_NAME,
    device=DEVICE,
    compute_type=COMPUTE_TYPE,
    download_root="/models",
)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "device": DEVICE}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        segments, info = model.transcribe(tmp.name, beam_size=5, vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments)
    return {"text": text.strip(), "language": info.language}
