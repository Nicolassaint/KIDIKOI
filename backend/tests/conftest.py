import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
from app.main import app
from app.services.audio_processor import AudioProcessor


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def audio_processor():
    return AudioProcessor()


@pytest.fixture
def test_audio_file():
    # Créer un fichier audio de test temporaire
    test_file_path = Path(__file__).parent / "fixtures" / "test_audio.wav"

    # Assurez-vous que le dossier fixtures existe
    test_file_path.parent.mkdir(exist_ok=True)

    # Si le fichier n'existe pas, créez un fichier audio factice
    if not test_file_path.exists():
        import wave
        import struct

        with wave.open(str(test_file_path), "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(44100)
            for _ in range(44100):  # 1 seconde de silence
                value = struct.pack("h", 0)
                f.writeframes(value)

    yield str(test_file_path)

    # Nettoyage (optionnel)
    # os.remove(str(test_file_path))
