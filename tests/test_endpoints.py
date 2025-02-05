import pytest
from fastapi.testclient import TestClient
from pathlib import Path

def test_root_endpoint(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200

def test_transcribe_invalid_file_format(test_client: TestClient):
    # Test avec un fichier texte
    files = {"file": ("test.txt", b"some content", "text/plain")}
    response = test_client.post("/api/v1/transcribe/", files=files)
    assert response.status_code == 400
    assert "File format not supported" in response.json()["detail"]

@pytest.mark.asyncio
async def test_transcribe_valid_file(test_client: TestClient, test_audio_file):
    with open(test_audio_file, "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        response = test_client.post("/api/v1/transcribe/", files=files)
        assert response.status_code == 200
        assert "segments" in response.json() 