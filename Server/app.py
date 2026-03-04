"""
Jarvis AI — FastAPI Ana Uygulama

Beyin'in kapısı: n8n webhook'larından gelen istekleri karşılar,
async handler'a yönlendirir ve yanıtı döndürür.

Endpoints:
    POST /api/chat      — Sohbet isteği (n8n → Jarvis)
    GET  /api/health    — Sistem sağlık kontrolü
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from logging_config import get_logger, setup_logging
from Server.dependencies import SharedState, get_shared_state, set_shared_state
from Server.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
)
from settings import get_settings

logger = get_logger("server.app")


# ── Lifespan ───────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Uygulama ömür döngüsü yöneticisi.
    Startup: Logging, SharedState, HTTP client başlat.
    Shutdown: Kaynakları temizle.
    """
    settings = get_settings()

    # Logging altyapısını kur
    setup_logging(
        log_level=settings.log_level,
        log_format=settings.log_format,
    )

    # SharedState başlat
    state = get_shared_state()
    await state.startup()

    logger.info(
        "jarvis_brain_online",
        host=settings.api_host,
        port=settings.api_port,
        ollama_url=settings.ollama_base_url,
        qdrant_url=settings.qdrant_url,
    )

    yield

    # Shutdown
    await state.shutdown()
    logger.info("jarvis_brain_offline")


# ── App Factory ────────────────────────────────────────────


def create_app() -> FastAPI:
    """FastAPI uygulama instance'ı oluştur."""
    settings = get_settings()

    app = FastAPI(
        title="Jarvis AI Brain",
        description="Dağıtık Jarvis AI Asistanı — Beyin ve İşlem Merkezi",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(_router)

    return app


# ── Router ─────────────────────────────────────────────────

from fastapi import APIRouter

_router = APIRouter(prefix="/api", tags=["Jarvis API"])


@_router.post(
    "/chat",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Sohbet isteği",
    description="n8n veya harici istemciden gelen mesajı işler ve Jarvis yanıtı döndürür.",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Ana sohbet endpoint'i.

    Akış: ChatRequest → async_handler → ChatResponse
    """
    start = time.perf_counter()
    state = get_shared_state()

    try:
        # Kullanıcıya özel memory instance al
        memory = state.session_manager.get_or_create(request.user_id)

        # Async handler'ı çağır (Faz 2'de implement edilecek)
        from Core.async_handler import process_input_async

        result = await process_input_async(
            user_input=request.message,
            memory=memory,
            user_id=request.user_id,
            settings=state.settings,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "chat_processed",
            user_id=request.user_id,
            platform=request.platform,
            action=result.get("action_taken"),
            elapsed_ms=round(elapsed_ms, 1),
        )

        return ChatResponse(
            response=result["response"],
            session_id=request.user_id,
            action_taken=result.get("action_taken"),
            processing_time_ms=round(elapsed_ms, 1),
        )

    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error(
            "chat_error",
            user_id=request.user_id,
            error=str(exc),
            elapsed_ms=round(elapsed_ms, 1),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"İşlem sırasında hata oluştu: {exc}",
        )


@_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Sistem sağlık kontrolü",
)
async def health() -> HealthResponse:
    """
    Sistem bileşenlerinin erişilebilirlik durumunu kontrol eder.
    """
    state = get_shared_state()
    settings = state.settings

    # Ollama erişilebilirlik kontrolü
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    # Qdrant erişilebilirlik kontrolü
    qdrant_ok = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.qdrant_url}/collections")
            qdrant_ok = resp.status_code == 200
    except Exception:
        pass

    # Genel durum
    if ollama_ok and qdrant_ok:
        status = "healthy"
    elif ollama_ok:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        uptime_seconds=round(state.uptime, 1),
        ollama_reachable=ollama_ok,
        qdrant_reachable=qdrant_ok,
    )


# ── App Instance ───────────────────────────────────────────

app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )
