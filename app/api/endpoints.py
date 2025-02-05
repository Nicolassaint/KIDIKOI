from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Request
from ..core.models import TranscriptionResponse
from ..services.audio_processor import AudioProcessor
import tempfile
import os

router = APIRouter()
audio_processor = AudioProcessor()

@router.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # Le timeout devrait être configuré au niveau du serveur
    
    if not file.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="File format not supported")
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        result = await audio_processor.process_audio_file(temp_file_path)
        return result
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path) 