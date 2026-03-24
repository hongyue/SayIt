# AGENTS.md - SayIt

## Project Overview

Public Text-to-Speech Web App using Python FastAPI and Kokoro TTS (82M parameter model).
No authentication required. Frontend served as static files via Vue 3 CDN.

## Quick Start

```bash
# Install dependencies and create .venv
uv sync

# Run dev server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at http://localhost:8000. Run from project root.

### System Dependencies (non-Python)

```bash
# macOS
brew install espeak-ng ffmpeg

# Debian/Ubuntu
apt install -y espeak-ng ffmpeg
```

- `espeak-ng` — required for non-English voices
- `ffmpeg` — required for MP3 output

## Project Structure

```
SayIt/
├── AGENTS.md
├── pyproject.toml               # Project metadata, deps, uv config
├── .python-version              # Python 3.12
├── uv.lock                      # Lockfile (auto-generated, commit to VCS)
├── .venv/                       # Virtualenv (auto-generated, git-ignored)
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, lifespan, static serving
│   │   ├── config.py            # Voice list, constants (CHUNK_SIZE=2000, SAMPLE_RATE=24000)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic: TTSRequest (text, voice, speed, format)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── tts.py           # Endpoints: GET /api/voices, POST /api/generate
│   │   └── services/
│   │       ├── __init__.py
│   │       └── tts_service.py   # Kokoro pipeline, auto-chunking, audio generation
│   └── frontend/
│       └── index.html           # Vue 3 CDN app (single file)
├── img/
├── LICENSE.md
└── .gitignore
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

## Build / Lint / Test Commands

```bash
# Install dependencies (creates .venv, generates uv.lock)
uv sync

# Run dev server with auto-reload
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run server (production)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

No test suite exists. No linting/type-checking tooling is configured (no pytest, ruff, mypy, etc.).
To verify changes, use the manual curl tests below:

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

## Code Style Guidelines

### Imports
- Standard library first, then third-party, then local (`app.*`)
- One blank line between import groups
- Prefer explicit imports over `from x import *`

### Formatting
- PEP 8, 4-space indentation
- No formatter/linter configured in project

### Type Hints
- Use for all function signatures (e.g., `def generate(self, text: str) -> bytes:`)
- Use `Optional[T]` from `typing` for nullable params
- Use `Literal` for constrained string choices (see `schemas.py`)

### Naming
- `snake_case` for functions, variables, module names
- `PascalCase` for classes
- Private/internal methods prefixed with `_` (e.g., `_generate_sync`, `_chunk_text`)

### Logging
- `logger = logging.getLogger(__name__)` at module level
- Use f-strings in log messages: `logger.info(f"TTS request: voice='{payload.voice}'")`
- Use `logger.error(..., exc_info=True)` for exception tracebacks

### Error Handling
- Raise `ValueError` for invalid input in services
- Use `HTTPException(status_code=400)` for bad requests in routers
- Use `HTTPException(status_code=500)` for internal errors in routers
- Catch broad `Exception` in route handlers, log with `exc_info=True`

### Async Patterns
- Use `asyncio.get_event_loop().run_in_executor(None, ...)` for CPU-bound Kokoro calls
- Sync implementations prefixed with `_` (e.g., `_generate_sync`)
- Use `@asynccontextmanager` for lifespan events
- Streaming uses `threading.Thread` + `asyncio.Queue` pattern

### Pydantic Models
- Define in `app/models/schemas.py`
- Use `Field(...)` with validation constraints (`min_length`, `max_length`, `ge`, `le`)
- Use `Literal` for enum-like fields

## Key Implementation Notes

### Auto-Chunking
Text > 2000 characters is automatically split on sentence boundaries:
- Splits on `.`, `!`, `?` followed by whitespace
- Long sentences are split at CHUNK_SIZE (2000 chars)
- Audio chunks are concatenated seamlessly via `np.concatenate`

### Voice Languages
Supported: US English (20), UK English (8), Japanese (5), Mandarin Chinese (8), Spanish (3), French (1), Hindi (4), Italian (2), Brazilian Portuguese (3). Korean is NOT supported.

### Audio Format
- WAV: 24kHz, 16-bit PCM, mono
- MP3: 192kbps bitrate (requires ffmpeg + pydub)

### Dependencies
All dependencies are declared in `pyproject.toml`. Core: kokoro, torch, fastapi, uvicorn, pydantic, soundfile, numpy, pydub.
Chinese: pypinyin, cn2an, jieba.
Japanese: fugashi, jaconv, mojimoji, unidic-lite, pyopenjtalk.

### System Requirements
- Python 3.10-3.12
- uv (package manager) — manages `.venv/` and `uv.lock`
- espeak-ng (for non-English languages)
- ffmpeg (for MP3 support)
- On Linux: torch is installed as CPU-only (from PyTorch CPU index)
- On macOS: torch includes MPS (Apple GPU) support

## Common Tasks

### Add New Voice
Edit `src/app/config.py`, add voice to `VOICES` dict with name, label, gender. The `VOICE_LANG_MAP` is auto-derived.

### Add New Endpoint
Create function in `src/app/routers/tts.py` with `@router.get()` or `@router.post()`.

### Add New Router
Create file in `src/app/routers/`, import and register in `src/app/main.py` via `app.include_router()`.

### Add New Dependency
```bash
uv add <package-name>       # adds to pyproject.toml and updates uv.lock
uv remove <package-name>    # removes dependency
uv sync                     # sync .venv with pyproject.toml
```
