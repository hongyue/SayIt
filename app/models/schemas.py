from pydantic import BaseModel, Field
from typing import Literal


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="Text to convert to speech")
    voice: str = Field(default="af_heart", description="Voice name")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    format: Literal["wav", "mp3"] = Field(default="wav", description="Output audio format")
