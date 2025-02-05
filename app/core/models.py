from pydantic import BaseModel
from typing import List, Dict

class Timestamp(BaseModel):
    start: float
    end: float

class Segment(BaseModel):
    timestamp: Timestamp
    speaker: str
    text: str

class TranscriptionResponse(BaseModel):
    segments: List[Segment] 