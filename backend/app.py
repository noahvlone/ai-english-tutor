import os
import base64
import tempfile
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydub import AudioSegment
import speech_recognition as sr
import pyttsx3
import httpx

HF_TOKEN = os.getenv("HF_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

app = FastAPI()

tts_engine = pyttsx3.init()
try:
  tts_engine.setProperty('rate', 160)
except Exception:
  pass

async def text_to_speech_bytes(text: str) -> bytes:
  with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    tmpfname = f.name
  def run_and_save():
    tts_engine.save_to_file(text, tmpfname)
    tts_engine.runAndWait()
  loop = asyncio.get_event_loop()
  await loop.run_in_executor(None, run_and_save)
  data = open(tmpfname, "rb").read()
  try:
    os.remove(tmpfname)
  except:
    pass
  return data

async def speech_to_text_from_wav_bytes(wav_bytes: bytes) -> str:
  r = sr.Recognizer()
  with tempfine.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    fname = f.name
    f.write(wav_bytes)
  audio = sr.AudioFile(fname)
  with audio as source:
    audio_data = r.record(source)
  text = ""
  try:
    text = r.recognize_google(audio_data)
  except sr.UnknownValueError:
    text = ""
  except sr.RequestError:
    text = ""
  try:
    os.remove(fname)
  except:
    pass
  return text

async def call_llm_reply(prompt: str) -> str:
  if OPENROUTER_KEY:
    url = "https://api.openrouter.ai/v1/chat/completions"
    payload = {
      "model": "z-ai/glm-4.5-air:free"
      "message": [{"role": "user", "content": prompt}],
      "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
    async with httpx.AsyncClient(timeout=50) as client:
      r = await client.post(url, json=payload, headers=headers)
      try:
        return r.json()["choices"][0]["message"]["content"].strip()
      except Exception:
        return "maaf saya ngga bisa jawab sekarang"
  if HF_TOKEN: 
    async with httpx.AsyncClient(timeout=50) as client:
      headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
      return f"tutor: saya menerima: {prompt}"
  return f"I heard: '{prompt}', Good! try to expand your sentence by adding more detail, for example: 'i like to study english every day because it helps me communicate'"

@app.websocket("/ws/audio")
async def websocket_endpoint(ws: WebSocket):
  await ws.accept()
  print("Client connected")
  audio_chunks = []
  try:
    while True:
      msg = await ws.receive_json()
      msg_type = msg.get("type")
      if msg_type == "audio_chunk":
        b64 = msg.get("data")
        if b64:
          audio_chunks.append(base64.b64decode(b64))
      elif msg_type == "utterance_end":
        if not audio_chunks:
          await ws.send_json({"type": "error", "message": "no audio receive"})
          continue 
        combined = b"".join(audio_chunks)
        transcript = await speech_to_text_from_wav_bytes(combined)
        if not transcript:
          transcript = "(tidak terdeteksi suara)"
        await ws.send_json({"type": "transcript", "text": transcript})
        reply_text = await call_llm_reply(transcript)
        audio_bytes = await text_to_speech_bytes(reply_text)
        audio_b64 = base64.b64encode(audio_byteds).decode()
        await ws.send_json({"type": "assistant_audio", "audio_b64": audio_b64, "text": reply_text})
        audio_chunks = []
      elif msg_type == "close":
        await ws.close()
        return
  except WebSocketDisconnect:
    print("client disconnected")
  except Exception as e:
    print("error in websocket", e)
    try:
      await ws.send_json({"type": "error", "message": str(e)})
    except:
      pass

if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=7000)
