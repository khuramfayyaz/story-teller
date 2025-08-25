from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from gtts import gTTS
import uuid, os, re

app = FastAPI()

# CORS: allow your S3 site to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # (Optional) replace "*" with your S3 website origin for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Where MP3s are saved
os.makedirs("audio", exist_ok=True)

# ---- Load models (CPU-friendly) ----
# 1) English story generator (small; OK on t3.micro)
generator = pipeline("text-generation", model="gpt2")   # ~500-900 words via max_new_tokens

# 2) Translators
#   ur -> en (if user gives Urdu title)
translator_ur_en = pipeline("translation", model="Helsinki-NLP/opus-mt-ur-en")
#   en -> ur (final story must be in Urdu)
translator_en_ur = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ur")

def contains_urdu(text: str) -> bool:
    """Detect any Urdu/Arabic script characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/story")
async def story(title: str = Form(...)):
    """
    - Accept title (Urdu or English)
    - If Urdu title: translate to English for the generator
    - Generate ~3–5 minute story in English
    - Translate full story to Urdu
    - Make Urdu MP3 with gTTS
    """
    # ---- Normalize title to English for the generator ----
    if contains_urdu(title):
        try:
            title_en = translator_ur_en(title)[0]["translation_text"]
        except Exception:
            title_en = "A children's story"  # fallback
    else:
        title_en = title

    # ---- Generate English story ----
    prompt = (
        f"Write a wholesome children's story titled '{title_en}'. "
        "Audience: families in South Asia. Avoid violence. "
        "Keep it engaging with short paragraphs and simple language. "
        "Length: around 500–900 words."
    )
    out = generator(
        prompt,
        max_new_tokens=650,            # ~3–5 minutes
        do_sample=True,
        temperature=0.9,
        top_p=0.95,
        num_return_sequences=1,
        pad_token_id=50256,            # GPT-2 EOS as pad
        eos_token_id=50256
    )
    story_en = out[0]["generated_text"]

    # Remove the prompt if the model echoed it
    if story_en.startswith(prompt):
        story_en = story_en[len(prompt):].strip()

    # ---- Translate to Urdu ----
    try:
        story_ur = translator_en_ur(story_en)[0]["translation_text"]
    except Exception:
        # fallback: still produce something
        story_ur = f"عنوان: {title}\n\n(اردو ترجمہ عارضی طور پر دستیاب نہیں)\n\n{story_en}"

    # Prepend Urdu title if user gave one
    heading = f"عنوان: {title}\n\n" if title else ""
    final_urdu_text = f"{heading}{story_ur}".strip()

    # ---- TTS (Urdu) ----
    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join("audio", filename)
    tts = gTTS(text=final_urdu_text, lang="ur")
    tts.save(path)

    return JSONResponse({"text": final_urdu_text, "audio": filename})

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join("audio", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return JSONResponse({"error": "File not found"}, status_code=404)
