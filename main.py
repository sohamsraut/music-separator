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

@app.get("/test")
def test():
  return {"message": "hello world"}

@app.get("/test-wav")
def test_wav():
  test_path = "stems\\46ffeddf-514c-4d75-824e-5fc369b53f27\crawling/accompaniment.wav"
  return FileResponse(test_path, media_type="audio/wav")

