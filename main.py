# server-side code
import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from spleeter.separator import Separator

# app
app = FastAPI()

# For local testing allow cors
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"], # Change this to change origin (currently allows all)
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# temp dir to store separated stems
BASE_STEMS_DIR = "stems"
os.makedirs(BASE_STEMS_DIR, exist_ok=True)

#mount static filesys for stems
app.mount("/stems", StaticFiles(directory=BASE_STEMS_DIR), name="stems")

@app.get("/test")
def test():
  return {"message": "hello world"}

@app.get("/test-wav")
def test_wav():
  test_path = "stems\\46ffeddf-514c-4d75-824e-5fc369b53f27\crawling/accompaniment.wav"
  return FileResponse(test_path, media_type="audio/wav")

@app.post("/separate")
async def separate_audio(
    file: UploadFile = File(...),
    stems: int = Form(4)
):
    # Generate a unique ID for this separation session to avoid collisions
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(BASE_STEMS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    input_path = os.path.join(session_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    model_name = f"spleeter:{stems}stems"
    separator = Separator(model_name)
    separator.separate_to_file(input_path, session_dir)

    # The separated stems will be in a folder named after the input file (without extension)
    song_name = os.path.splitext(file.filename)[0]
    stems_folder = os.path.join(session_dir, song_name)

    if not os.path.exists(stems_folder):
        return JSONResponse({"error": "Separation failed."}, status_code=500)

    # List WAV files and build URLs
    stems_files = []
    for filename in os.listdir(stems_folder):
        if filename.endswith(".wav"):
            url_path = f"./stems/{session_id}/{song_name}/{filename}"
            # url_path = url_path.replace("/", "/")  # fix slashes for URLs
            stems_files.append({
                "name": os.path.splitext(filename)[0],
                "url": url_path
            })

    return {"stems": stems_files}