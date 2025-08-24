from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from gtts import gTTS
import os
import uuid

app = FastAPI()

# Health check
@app.get("/health")
def health():
    return {"ok": True}

# Generate Urdu story (dummy example for now)
@app.post("/story")
def story(title: str = Form(...)):
    # For now just make a placeholder story in Urdu
    # Later we can connect an LLM to generate dynamic stories
    story_text = f"یہ ایک دلچسپ کہانی ہے جس کا عنوان {title} ہے۔ ایک وقت کی بات ہے، ایک شہر میں لوگ امن اور سکون سے رہتے تھے۔ اچانک ایک واقعہ ہوا جس نے سب کی زندگی بدل دی۔ کہانی تین منٹ تک جاری رہے گی، جس میں سبق یہ ہے کہ انسان کو ہمیشہ صبر اور محنت کرنی چاہیے۔"

    # Save audio
    filename = f"{uuid.uuid4().hex}.mp3"
    tts = gTTS(story_text, lang="ur")
    tts.save(filename)

    return {
        "text": story_text,
        "audio": filename
    }

# Serve the audio file
@app.get("/audio/{filename}")
def get_audio(filename: str):
    file_path = os.path.join(".", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    return JSONResponse(content={"error": "File not found"}, status_code=404)
