# Importe les outils nécessaires
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import time

# Initialise l'application
app = FastAPI(title="DocVox API")

# Autorise les requêtes depuis n'importe où (pour le front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Cache simplifié en mémoire
cache = {}

async def fake_ai_processing(content: bytes, sentences: int) -> dict:
    """Fonction factice qui simule l'IA (à remplacer par ton vrai code)"""
    await asyncio.sleep(1)  # Simule un traitement de 1 seconde
    return {
        "summary": "Ceci est un résumé généré par l'IA",
        "audio_file": "audio.mp3",
        "summary_file": "resume.txt"
    }

@app.post("/process/")
async def process_file(
    file: UploadFile = File(...),  # Reçoit le fichier
    max_sentences: int = Form(5),  # Reçoit le nombre de phrases
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        # 1. Vérifie le cache
        file_content = await file.read()
        cache_key = hashlib.md5(file_content + str(max_sentences).encode()).hexdigest()
        
        if cache_key in cache:
            return cache[cache_key]
        
        # 2. Traitement "IA"
        start_time = time.time()
        result = await fake_ai_processing(file_content, max_sentences)
        processing_time = time.time() - start_time
        
        # 3. Mise en cache (60 secondes)
        cache[cache_key] = result
        background_tasks.add_task(lambda: cache.pop(cache_key, None))
        
        return {**result, "processing_time": processing_time}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    """Endpoint pour garder Render actif"""
    return {"status": "OK", "timestamp": time.time()}