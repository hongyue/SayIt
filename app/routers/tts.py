import logging
import io
import json
import threading
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.models.schemas import TTSRequest
from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/voices")
async def get_voices():
    return tts_service.get_voices()


@router.post(
    "/generate",
    responses={
        200: {
            "content": {
                "audio/wav": {},
                "audio/mpeg": {},
            }
        }
    },
)
async def generate_tts(payload: TTSRequest):
    logger.info(f"TTS request: voice='{payload.voice}', speed={payload.speed}, format={payload.format}")

    try:
        audio_bytes = await tts_service.generate(
            text=payload.text,
            voice=payload.voice,
            speed=payload.speed,
            output_format=payload.format,
        )

        media_type = "audio/mpeg" if payload.format == "mp3" else "audio/wav"
        return StreamingResponse(io.BytesIO(audio_bytes), media_type=media_type)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")


@router.post("/generate/stream")
async def generate_tts_stream(payload: TTSRequest, request: Request):
    logger.info(f"TTS stream request: voice='{payload.voice}', speed={payload.speed}")
    cancel_event = threading.Event()

    async def event_generator():
        try:
            async for chunk_b64 in tts_service.generate_stream(
                text=payload.text,
                voice=payload.voice,
                speed=payload.speed,
                cancel_event=cancel_event,
            ):
                if await request.is_disconnected():
                    logger.info("Client disconnected, cancelling generation")
                    cancel_event.set()
                    return
                event_data = json.dumps({"audio": chunk_b64})
                yield f"data: {event_data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"TTS stream error: {e}", exc_info=True)
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
        finally:
            cancel_event.set()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
