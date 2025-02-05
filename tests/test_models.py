import pytest
from app.core.models import Timestamp, Segment, TranscriptionResponse

def test_timestamp_model():
    timestamp = Timestamp(start=0.0, end=1.0)
    assert timestamp.start == 0.0
    assert timestamp.end == 1.0

def test_segment_model():
    segment = Segment(
        timestamp=Timestamp(start=0.0, end=1.0),
        speaker="SPEAKER_01",
        text="Hello, world!"
    )
    assert segment.timestamp.start == 0.0
    assert segment.timestamp.end == 1.0
    assert segment.speaker == "SPEAKER_01"
    assert segment.text == "Hello, world!"

def test_transcription_response_model():
    response = TranscriptionResponse(
        segments=[
            Segment(
                timestamp=Timestamp(start=0.0, end=1.0),
                speaker="SPEAKER_01",
                text="Hello"
            ),
            Segment(
                timestamp=Timestamp(start=1.0, end=2.0),
                speaker="SPEAKER_02",
                text="World"
            )
        ]
    )
    assert len(response.segments) == 2
    assert response.segments[0].text == "Hello"
    assert response.segments[1].text == "World"

def test_invalid_timestamp():
    with pytest.raises(ValueError):
        Timestamp(start="invalid", end=1.0)

def test_invalid_segment():
    with pytest.raises(ValueError):
        Segment(
            timestamp="invalid",
            speaker="SPEAKER_01",
            text="Hello"
        ) 