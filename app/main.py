import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import tts
from app.services.tts_service import tts_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")
    tts_service.cleanup()


app = FastAPI(
    title="SayIt API",
    description="Public Text-to-Speech API powered by Kokoro",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts.router, prefix="/api")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("frontend/index.html")
