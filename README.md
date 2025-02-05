# API de Transcription Audio

Une API FastAPI pour la transcription audio avec détection des locuteurs, utilisant Whisper et Pyannote.

## 🚀 Fonctionnalités

- Transcription audio multilingue
- Détection et identification des locuteurs
- Support des formats audio : WAV, MP3, M4A
- API RESTful avec documentation automatique

## 🛠️ Prérequis

- Python 3.8+
- PyTorch
- CUDA (recommandé pour de meilleures performances)
- Token Hugging Face (pour pyannote.audio)

## ⚙️ Installation

1. Clonez le repository : 

```	bash
git clone [url-du-repo]
cd [nom-du-repo]
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet :

``` bash
HF_TOKEN=votre_token_hugging_face
MODEL_NAME=openai/whisper-large-v3-turbo
DIARIZATION_MODEL=pyannote/speaker-diarization-3.1
```

## 🚀 Démarrage

Lancez l'application avec :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8502
```

L'API sera accessible à `http://localhost:8502`
Documentation Swagger UI : `http://localhost:8502/docs`

## 📝 Utilisation

Pour transcrire un fichier audio :

```bash
curl -X POST "http://localhost:8502/api/v1/transcribe/" \
-H "accept: application/json" \
-H "Content-Type: multipart/form-data" \
-F "file=@votre_fichier_audio.mp3"
```

### Format de réponse
       
```json
{
    "segments": [
        {
            "timestamp": {
                "start": 0.0,
                "end": 2.5
            },
            "speaker": "SPEAKER_01",
            "text": "Texte transcrit..."
        }
    ]
}
```

## 🔑 Configuration

Les paramètres de configuration sont gérés dans `app/core/config.py` :
- `HF_TOKEN` : Token Hugging Face
- `MODEL_NAME` : Modèle Whisper utilisé
- `DIARIZATION_MODEL` : Modèle de diarization utilisé

## 🛠️ Architecture

- `app/main.py` : Point d'entrée de l'application
- `app/api/endpoints.py` : Routes de l'API
- `app/core/models.py` : Modèles Pydantic
- `app/services/audio_processor.py` : Logique de traitement audio
- `app/core/config.py` : Configuration de l'application
