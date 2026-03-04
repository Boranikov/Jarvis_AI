"""
Jarvis AI — Yapısal Logging Konfigürasyonu (structlog)

İki mod:
  - console: Renkli, okunabilir (geliştirme)
  - json:    Structured JSON (production)

Kullanım:
    from logging_config import get_logger
    logger = get_logger("brain.intent")
    logger.info("intent_parsed", action="play_music", confidence=0.98)
"""

import logging
import sys
from typing import Any

import structlog

_CONFIGURED: bool = False


def setup_logging(log_level: str = "DEBUG", log_format: str = "console") -> None:
    """
    Uygulama geneli structlog yapılandırması.

    Args:
        log_level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Çıktı formatı — "console" (renkli) veya "json"
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    numeric_level: int = getattr(logging, log_level.upper(), logging.DEBUG)

    # Shared processors (her iki format için ortak)
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        # Production: JSON output
        renderer = structlog.processors.JSONRenderer(ensure_ascii=False)
    else:
        # Development: renkli console output
        renderer = structlog.dev.ConsoleRenderer(
            colors=sys.stderr.isatty(),
            pad_event=40,
        )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # stdlib logging handler (FastAPI / uvicorn / üçüncü parti logları da yakalar)
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Mevcut handler'ları temizle (çift log önleme)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(numeric_level)
    root_logger.addHandler(handler)

    # Gürültülü kütüphaneleri sustur
    for noisy in ("httpx", "httpcore", "uvicorn.access", "watchfiles"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Modül bazlı structlog logger oluştur.

    Args:
        name: Logger ismi (örn: "brain.intent", "server.app")

    Returns:
        Bound structlog logger instance

    Kullanım:
        logger = get_logger("integrations.qdrant")
        logger.info("connected", url="http://192.168.1.186:6333")
    """
    return structlog.get_logger(name)
