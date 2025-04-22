from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import time
import asyncio
import io
import pdfplumber
import docx
from gtts import gTTS
import os
import uuid

app = FastAPI(title="DocVox API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

cache = {}

async def extract_text_pdf(content: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = "Impossible d'extraire le texte du PDF."
    return text

async def extract_text_docx(content: bytes) -> str:
    text = ""
    try:
        doc = docx.Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception:
        text = "Impossible d'extraire le texte du DOCX."
    return text

async def extract_text_txt(content: bytes) -> str:
    try:
        text = content.decode(errors="ignore")
    except Exception:
        text = "Impossible de lire le fichier TXT."
    return text

async def fake_ai_processing(content: bytes, filename: str, sentences: int) -> dict:
    # Détection du type de fichier par extension
    text = ""
    if filename.endswith('.pdf'):
        text = await extract_text_pdf(content)
    elif filename.endswith('.docx'):
        text = await extract_text_docx(content)
    elif filename.endswith('.txt'):
        text = await extract_text_txt(content)
    else:
        text = "Format de fichier non supporté."

    # Résumé factice : premières phrases
    if text and text not in [
        "Impossible d'extraire le texte du PDF.",
        "Impossible d'extraire le texte du DOCX.",
        "Impossible de lire le fichier TXT.",
        "Format de fichier non supporté."
    ]:
        phrases = [p.strip() for p in text.replace('\n', ' ').split('.') if p.strip()]
        summary = '. '.join(phrases[:sentences]) + ('.' if phrases else '')
        if not summary.strip():
            summary = "Aucune phrase trouvée dans le document."
    else:
        summary = text

    # Génération audio MP3 avec gTTS
    audio_filename = ""
    try:
        if summary and "Impossible" not in summary and "Aucune phrase trouvée" not in summary:
            unique_id = str(uuid.uuid4())[:8]
            audio_filename = f"audio_{unique_id}.mp3"
            tts = gTTS(summary, lang="fr")
            tts.save(audio_filename)
    except Exception:
        audio_filename = ""

    return {
        "summary": summary,
        "original_text": text,
        "audio_file": audio_filename,
        "summary_file": ""  # À compléter si tu veux générer un fichier texte
    }

async def expire_cache_key(key: str, delay: int = 60):
    await asyncio.sleep(delay)
    cache.pop(key, None)

@app.post("/process/")
async def process_file(
    file: UploadFile = File(...),
    max_sentences: int = Form(5),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        file_content = await file.read()
        cache_key = hashlib.md5(file_content + str(max_sentences).encode()).hexdigest()

        if cache_key in cache:
            return cache[cache_key]

        start_time = time.time()
        result = await fake_ai_processing(file_content, file.filename.lower(), max_sentences)
        processing_time = time.time() - start_time

        cache[cache_key] = {**result, "processing_time": processing_time}
        background_tasks.add_task(expire_cache_key, cache_key, 60)

        return {**result, "processing_time": processing_time}

    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "OK", "timestamp": time.time()}
