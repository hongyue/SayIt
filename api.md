# API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Vue frontend |
| GET | `/api/voices` | List all available voices |
| POST | `/api/generate` | Generate complete audio (returns WAV/MP3) |
| POST | `/api/generate/stream` | Stream audio chunks via SSE |

## POST /api/generate

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

## POST /api/generate/stream

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