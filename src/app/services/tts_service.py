import logging
import io
import re
import asyncio
import gc
import base64
import numpy as np
import soundfile as sf
from kokoro import KPipeline
from pydub import AudioSegment
from typing import Optional

from app.config import VOICE_LANG_MAP, CHUNK_SIZE, SAMPLE_RATE

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self):
        self.pipelines: dict[str, KPipeline] = {}

    def _get_pipeline(self, lang_code: str) -> KPipeline:
        if lang_code not in self.pipelines:
            logger.info(f"Loading Kokoro pipeline for lang_code='{lang_code}'")
            self.pipelines[lang_code] = KPipeline(lang_code=lang_code)
        return self.pipelines[lang_code]

    def _split_cjk_sentences(self, text: str) -> list[str]:
        parts = re.split(r"([。！？])", text)
        segments = []
        for i in range(0, len(parts), 2):
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            if sentence.strip():
                segments.append(sentence.strip())
        if not segments:
            segments = [text[i : i + 300] for i in range(0, len(text), 300)]
        return segments

    def _generate_cjk_audio(self, pipeline, text: str, voice: str, speed: float):
        pack = pipeline.load_voice(voice).to(pipeline.model.device)
        sentences = self._split_cjk_sentences(text)
        logger.info(f"CJK text: {len(text)} chars -> {len(sentences)} sentences")

        for sentence in sentences:
            ps, _ = pipeline.g2p(sentence)
            if not ps:
                continue

            phoneme_chunks = []
            if len(ps) <= 510:
                phoneme_chunks.append(ps)
            else:
                clauses = re.split(r"([，；])", sentence)
                for i in range(0, len(clauses), 2):
                    clause = clauses[i]
                    if i + 1 < len(clauses):
                        clause += clauses[i + 1]
                    if not clause.strip():
                        continue
                    cps, _ = pipeline.g2p(clause)
                    if not cps:
                        continue
                    if len(cps) <= 510:
                        phoneme_chunks.append(cps)
                    else:
                        for j in range(0, len(cps), 510):
                            phoneme_chunks.append(cps[j : j + 510])

            for ps_chunk in phoneme_chunks:
                output = KPipeline.infer(pipeline.model, ps_chunk, pack, speed)
                if output.audio is not None and len(output.audio) > 0:
                    audio_dur = len(output.audio) / SAMPLE_RATE
                    logger.info(
                        f"Phoneme chunk: {len(ps_chunk)} phonemes, "
                        f"{len(output.audio)} samples, {audio_dur:.2f}s"
                    )
                    yield output.audio.cpu()

    def _chunk_text(self, text: str) -> list[str]:
        if len(text) <= CHUNK_SIZE:
            return [text]

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= CHUNK_SIZE:
                current_chunk = (
                    f"{current_chunk} {sentence}".strip() if current_chunk else sentence
                )
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(sentence) > CHUNK_SIZE:
                    sub_parts = [
                        sentence[i : i + CHUNK_SIZE]
                        for i in range(0, len(sentence), CHUNK_SIZE)
                    ]
                    chunks.extend(sub_parts[:-1])
                    current_chunk = sub_parts[-1]
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _generate_sync(self, text: str, voice: str, speed: float) -> np.ndarray:
        lang_code = VOICE_LANG_MAP.get(voice, "a")
        pipeline = self._get_pipeline(lang_code)
        chunks = self._chunk_text(text)

        audio_parts = []
        for chunk in chunks:
            if lang_code in ("z", "j"):
                for audio in self._generate_cjk_audio(pipeline, chunk, voice, speed):
                    audio_parts.append(audio)
            else:
                for _, _, audio in pipeline(chunk, voice=voice, speed=speed):
                    if audio is not None and len(audio) > 0:
                        audio_dur = len(audio) / SAMPLE_RATE
                        logger.info(
                            f"Pipeline chunk: {len(audio)} samples, {audio_dur:.2f}s"
                        )
                        audio_parts.append(audio)

        if not audio_parts:
            raise ValueError("No audio generated")

        total_dur = sum(len(a) for a in audio_parts) / SAMPLE_RATE
        logger.info(f"Total audio: {len(audio_parts)} parts, {total_dur:.2f}s")
        return np.concatenate(audio_parts)

    async def generate(
        self, text: str, voice: str, speed: float, output_format: str
    ) -> bytes:
        loop = asyncio.get_event_loop()
        audio_array = await loop.run_in_executor(
            None, self._generate_sync, text, voice, speed
        )

        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_array, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        wav_bytes = wav_buffer.getvalue()

        if output_format == "mp3":
            mp3_buffer = io.BytesIO()
            audio_segment = AudioSegment.from_wav(io.BytesIO(wav_bytes))
            audio_segment.export(mp3_buffer, format="mp3", bitrate="192k")
            return mp3_buffer.getvalue()

        return wav_bytes

    def _queue_audio(self, queue, audio, chunk_idx):
        if audio is not None and len(audio) > 0:
            audio_dur = len(audio) / SAMPLE_RATE
            logger.info(
                f"Stream chunk {chunk_idx}: {len(audio)} samples, {audio_dur:.2f}s"
            )
            wav_buffer = io.BytesIO()
            sf.write(wav_buffer, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
            queue.put_nowait(base64.b64encode(wav_buffer.getvalue()).decode("utf-8"))

    def _generate_stream_sync(
        self, text: str, voice: str, speed: float, queue, cancel_event=None
    ):
        lang_code = VOICE_LANG_MAP.get(voice, "a")
        pipeline = self._get_pipeline(lang_code)

        try:
            chunk_idx = 0
            if lang_code in ("z", "j"):
                chunks = self._chunk_text(text)
                for chunk in chunks:
                    for audio in self._generate_cjk_audio(
                        pipeline, chunk, voice, speed
                    ):
                        if cancel_event and cancel_event.is_set():
                            logger.info("Generation cancelled")
                            return
                        self._queue_audio(queue, audio, chunk_idx)
                        chunk_idx += 1
            else:
                for _, _, audio in pipeline(text, voice=voice, speed=speed):
                    if cancel_event and cancel_event.is_set():
                        logger.info("Generation cancelled")
                        return
                    if audio is not None and len(audio) > 0:
                        self._queue_audio(queue, audio, chunk_idx)
                        chunk_idx += 1
            logger.info(f"Stream complete: {chunk_idx} chunks sent")
        except Exception as e:
            queue.put_nowait(e)
        finally:
            queue.put_nowait(None)

    async def generate_stream(
        self, text: str, voice: str, speed: float, cancel_event=None
    ):
        import threading

        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def run_generator():
            self._generate_stream_sync(text, voice, speed, queue, cancel_event)

        thread = threading.Thread(target=run_generator)
        thread.start()

        try:
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                if isinstance(chunk, Exception):
                    raise chunk
                yield chunk
        finally:
            if cancel_event:
                cancel_event.set()
            thread.join(timeout=5)

    def get_voices(self) -> dict:
        from app.config import VOICES

        return VOICES

    def cleanup(self):
        self.pipelines.clear()
        gc.collect()


tts_service = TTSService()
