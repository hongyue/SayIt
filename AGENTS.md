# AGENTS.md - SayIt

## Project Overview

Public Text-to-Speech API server using Python FastAPI and Kokoro TTS (82M parameter model).
No authentication required. Frontend served as static files via Vue 3 CDN.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at http://localhost:8000

## Project Structure

```
sayit/
├── app/
│   ├── main.py              # FastAPI app, lifespan, static serving
│   ├── config.py            # Voice list, constants (CHUNK_SIZE=1500, SAMPLE_RATE=24000)
│   ├── models/
│   │   └── schemas.py       # Pydantic: TTSRequest (text, voice, speed, format)
│   ├── routers/
│   │   └── tts.py           # Endpoints: GET /api/voices, POST /api/generate
│   └── services/
│       └── tts_service.py   # Kokoro pipeline, auto-chunking, audio generation
├── frontend/
│   └── index.html           # Vue 3 CDN app (single file)
└── requirements.txt
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Vue frontend |
| GET | `/api/voices` | List all voices (54 voices, 9 languages) |
| POST | `/api/generate` | Generate speech (returns WAV/MP3 audio) |
| POST | `/api/generate/stream` | Stream audio chunks via SSE (real-time playback) |

### POST /api/generate Request Body
```json
{
  "text": "Hello world",
  "voice": "af_heart",
  "speed": 1.0,
  "format": "wav"
}
```

### POST /api/generate/stream Request Body
```json
{
  "text": "Hello world",
  "voice": "af_heart",
  "speed": 1.0
}
```

### SSE Response Format
```
data: {"audio": "base64_encoded_wav_chunk"}
data: {"audio": "base64_encoded_wav_chunk"}
data: [DONE]
```

## Code Style Guidelines

### Python Conventions
- **Imports**: Standard library first, then third-party, then local
- **Formatting**: PEP 8, 4-space indentation
- **Type hints**: Use for function signatures (e.g., `def generate(self, text: str) -> bytes:`)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Logging**: Use `logging.getLogger(__name__)` at module level

### Error Handling
- Raise `ValueError` for invalid input
- Use `HTTPException` in routers with appropriate status codes
- Log errors with `logger.error(..., exc_info=True)` for debugging

### Async Patterns
- Use `asyncio.get_event_loop().run_in_executor()` for CPU-bound tasks
- Keep sync functions separate (prefix with `_`)
- Use `@asynccontextmanager` for lifespan events

## Testing Commands

```bash
# Test voices endpoint
curl http://localhost:8000/api/voices

# Test WAV generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "voice": "af_heart"}' \
  -o output.wav

# Test MP3 generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "voice": "af_heart", "format": "mp3"}' \
  -o output.mp3

# Test Chinese voice
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "你好", "voice": "zf_xiaoxiao"}' \
  -o output_zh.wav

# Test Japanese voice
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは", "voice": "jf_alpha"}' \
  -o output_ja.wav

# Test streaming (SSE)
curl -X POST http://localhost:8000/api/generate/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "af_heart"}' \
  -N
```

## Key Implementation Notes

### Auto-Chunking
Text > 1500 characters is automatically split on sentence boundaries:
- Splits on `.`, `!`, `?` followed by whitespace
- Long sentences are split at CHUNK_SIZE (1500 chars)
- Audio chunks are concatenated seamlessly

### Voice Languages
Supported: US English (20), UK English (8), Japanese (5), Mandarin Chinese (8), Spanish (3), French (1), Hindi (4), Italian (2), Brazilian Portuguese (3)

Korean is NOT supported by Kokoro.

### Audio Format
- WAV: 24kHz, 16-bit PCM, mono
- MP3: 192kbps bitrate (requires ffmpeg)

## Dependencies

### Core
- kokoro>=0.9.4 (TTS model)
- fastapi>=0.100.0 (web framework)
- uvicorn[standard]>=0.20.0 (ASGI server)
- pydantic>=2.0.0 (validation)
- soundfile>=0.12.0 (audio I/O)
- numpy>=1.20.0 (array operations)
- pydub>=0.25.0 (MP3 conversion)

### Chinese Support
- pypinyin>=0.44.0, cn2an>=0.5.0, jieba>=0.42.0

### Japanese Support
- fugashi>=1.2.0, jaconv>=0.3.0, mojimoji>=0.0.13
- unidic-lite>=1.0.8, pyopenjtalk>=0.3.0

## System Requirements

- Python 3.10-3.12
- espeak-ng (for non-English languages)
- ffmpeg (for MP3 support)

## Common Tasks

### Add New Voice
Edit `app/config.py`, add voice to VOICES dict with name, label, gender.

### Add New Endpoint
Create function in `app/routers/tts.py` with `@router.get()` or `@router.post()`.
