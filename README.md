# Audio Separator App (Spleeter + FastAPI)

Separates components of music (stems) such as vocals, instrumental, drums, bass, etc. from an uploaded music file using [Spleeter](https://github.com/deezer/spleeter). You can **play each stem in the browser**, **play them all together**, and **download individual WAVs** with a single click.

> This README is written for beginners too—follow it step by step and you’ll have the app running locally. It also covers how to deploy to a remote server safely.


## How it works

### For the user

- Upload an audio file (`.mp3`, `.wav`, `.flac`, etc.)
- Choose number of stems:
  - 2 stems: vocal + instrumental
  - 4 stems: vocal + drums + bass + other instruments
  - 5 stems: vocal + drums + bass + piano + other instruments
- **Play stems in your browser** as soon as they are ready
- **Play All / Pause All** to hear the full mix from separated tracks
- **Download** each stem (crisp download icon)
- Built with **FastAPI** (Python) and **vanilla HTML/JS**

### For the developer (high-level summary)

1. **Frontend** (`index.html`): The browser uploads a file to the backend and renders audio players once stems are ready.
2. **Backend** (`main.py`): Receives the upload, runs **Spleeter** to separate the track, saves WAV files into a session folder, and returns URLs for those WAVs.
3. **Static serving**: The backend exposes a `/stems/...` folder so the browser can stream the generated WAVs.


## 📦 Project structure (suggested)

```
audio-separator/
│
├── backend/
│   ├── main.py              # FastAPI backend (Spleeter + static serving + CORS)
│   ├── requirements.txt     # Python deps
│   └── stems/               # Generated stems (auto-created)
│
└── frontend/
    └── index.html           # Web UI (upload + players + play-all + download icons)
```

You can place files wherever you want; just keep the paths consistent (see “Paths that work everywhere” below).

## 🛠 Prerequisites

- `python 3.8.x` (Spleeter is old and works best on 3.8.x, it does not have support for >=3.9 as of August 2025).
- `pip` (and optionally **conda** or **venv** for a clean environment).
- `ffmpeg` installed and available on your PATH (helps with audio formats).
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install ffmpeg`
  - Windows: download from https://www.gyan.dev/ffmpeg/builds/ and add `bin` to your PATH.

> I recommend creating a separate virtual env with `conda` for python 3.8, since if you run into `numpy`/build issues with Spleeter, this avoids dependency hell.

## Setup – Backend

From the `backend/` folder:

### 1) Create and activate a virtual environment
**venv (macOS/Linux/Windows):**
```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

**OR conda (Windows/macOS/Linux):**
```bash
conda create -n spleeter-env python=3.8 -y
conda activate spleeter-env
```

### 2) Install dependencies
Install:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
where `requirements.txt`:
```txt
fastapi           -> for web server
uvicorn           -> for server hosting
spleeter          -> for music splitting
python-multipart
```

### 3) Run the backend

```bash
uvicorn main:app --reload --port 8000
```
You should see Uvicorn logs and the API available at `http://127.0.0.1:8000`.

## Setup – Frontend

After the uvicorn backend is set up, open `frontend/index.html` to see the results.

> If you need **sample‑accurate sync** (like a DAW), switch to the **Web Audio API** (decode to AudioBuffers and schedule `start(when)` for all stems at the same time). The `<audio>` approach is simple but not sample‑perfect across all browsers/devices.

## API contract

`POST /separate` (multipart form-data)

- **Fields**
  - `file` → uploaded audio file
  - `stems` → `2 | 4 | 5`
- **Response (200 OK)**
```json
{
  "stems": [
    {"name": "vocals", "url": "/stems/<session>/<song>/vocals.wav"},
    {"name": "drums",  "url": "/stems/<session>/<song>/drums.wav"},
    {"name": "bass",   "url": "/stems/<session>/<song>/bass.wav"},
    {"name": "other",  "url": "/stems/<session>/<song>/other.wav"}
  ],
  "session": "<uuid>",
  "song": "my_track"
}
```

## Troubleshooting

### “CORS header ‘Access‑Control‑Allow‑Origin’ missing”
- Add the CORS middleware shown below.
- Make sure the frontend `fetch()` points to the correct backend URL.

### Stems appear but **audio won’t play** (shows 0:00)
- Open a stem URL directly in the browser—does it download and play?
- Ensure WAVs are non‑empty (check file sizes).
- Make sure the backend serves files from the **absolute** static path (we use `os.path.abspath` + `StaticFiles`).
- URLs must use forward slashes (`/`). We already do `replace("\\", "/")` in code.

### Backend returns 500 after separation
- Check the logs—often means paths are wrong or output folder isn’t found.
- Confirm Spleeter wrote to `session_dir/<song_name>/...` (Windows path issues are common).

### Spleeter install errors (numpy, TensorFlow, etc.)
- Use Python **3.8** in a fresh venv/conda env.
- Upgrade `pip setuptools wheel` before installing Spleeter.

### “File not found” when returning a ZIP
- If you later add a “Download all” ZIP: ensure `shutil.make_archive()` base name and folder are correct. Return the **full** path to the created file.

## CORS (Cross‑Origin Resource Sharing)

If you open `index.html` from `file://` or serve frontend from a different host/port, your browser enforces CORS. The backend snippet above enables permissive CORS for **development**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

In **production**, restrict `allow_origins` to your real frontend URL.

## Deploying to a server

- Keep `BASE_STEMS_DIR` configurable via `STEMS_DIR` env var (e.g., `/var/app/stems`).
- Use a process manager (e.g., `gunicorn` + `uvicorn.workers.UvicornWorker`, or `pm2` via `pm2 start uvicorn -- ...`).
- Put **Nginx** in front to serve `/stems` efficiently and reverse‑proxy `/separate` to Uvicorn.
- Lock down CORS to your real frontend origin.
- Schedule cleanup of old session folders to save disk space (cron or a background task).

##  Possible future extensions

- **Download All** button → backend zips the session folder and returns one file.
- **Web Audio API** mixing for sample‑accurate sync.
- **GPU acceleration** + switch to **Demucs** model for higher quality (more compute).
- **Progress UI** with WebSockets (so users can see real-time progress).
- **Auth/rate limiting** if making this public.

## Credits

- **Spleeter** by Deezer: https://github.com/deezer/spleeter
- **FastAPI**: https://fastapi.tiangolo.com/
- **Uvicorn** ASGI server

If you get stuck or want polish (ZIP download, Web Audio API sync, progress bar), open an issue or ask for a patch!
