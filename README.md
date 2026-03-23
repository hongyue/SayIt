# SayIt

A TTS Web App powered by [Kokoro TTS](https://github.com/hexgrad/kokoro) (82M parameter model).

<img src="img/screenshot.png" alt="description" width="600">

## Quick Start

### Prerequisites

- Python 3.10-3.12
- espeak-ng (for non-English languages)
- ffmpeg (for MP3 support)

#### macOS

```bash
brew install espeak-ng ffmpeg
```

#### Ubuntu/Debian

```bash
sudo apt-get install espeak-ng ffmpeg
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd sayit

# Install dependencies
pip install -r requirements.txt
```

### Start Server

```bash
# Development (with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server runs at **http://localhost:8000**

### Stop Server

Press `Ctrl+C` in the terminal where the server is running.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Vue frontend |
| GET | `/api/voices` | List all available voices |
| POST | `/api/generate` | Generate complete audio (returns WAV/MP3) |
| POST | `/api/generate/stream` | Stream audio chunks via SSE |

### POST /api/generate

Generate speech and return complete audio file.

**Request Body:**
```json
{
  "text": "Hello, world!",
  "voice": "af_heart",
  "speed": 1.0,
  "format": "wav"
}
```

**Response:** Audio file (`audio/wav` or `audio/mpeg`)

### POST /api/generate/stream

Stream audio chunks in real-time via Server-Sent Events.

**Request Body:**
```json
{
  "text": "Hello, world!",
  "voice": "af_heart",
  "speed": 1.0
}
```

**Response:** SSE stream
```
data: {"audio": "base64_encoded_wav_chunk"}
data: {"audio": "base64_encoded_wav_chunk"}
data: [DONE]
```

## Audio Format

- **WAV:** 24kHz, 16-bit PCM, mono
- **MP3:** 192kbps bitrate (requires ffmpeg)

## License

This project uses the Kokoro TTS model. Please refer to the [Kokoro license](https://github.com/hexgrad/kokoro) for model usage terms.
