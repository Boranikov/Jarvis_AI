"""
Jarvis AI — MCP Memory Tools

Qdrant vektörel hafızası üzerinden bilgi saklama ve geri çağırma araçları.
FastMCP @tool dekoratörü ile tanımlanır.
"""

from typing import Any

from MCP.tool_registry import mcp
from Config.logging_config import get_logger

logger = get_logger("mcp.tools.memory")

# Qdrant client referansı — uygulama başlangıcında set edilir
_qdrant_memory = None


def set_memory_client(client: Any) -> None:
    """QdrantMemory client referansını ayarla (lifespan'da çağrılır)."""
    global _qdrant_memory
    _qdrant_memory = client


@mcp.tool()
async def store_long_term_memory(
    text: str,
    category: str = "general",
    user_id: str = "system",
) -> str:
    """
    Bilgiyi Jarvis'in uzun vadeli hafızasına kaydet.

    Kullanıcının tercihlerini, önemli bilgileri ve bağlamı saklar.

    Args:
        text: Hatırlanacak bilgi metni
        category: Bilgi kategorisi (general, preference, fact, conversation)
        user_id: Bilgiyi kaydeden kullanıcı ID'si

    Returns:
        Başarı durumu mesajı
    """
    if _qdrant_memory is None:
        return "Hafıza sistemi henüz başlatılmadı."

    try:
        point_id = await _qdrant_memory.store(
            text=text,
            category=category,
            user_id=user_id,
        )
        logger.info("memory_stored_via_tool", point_id=point_id, category=category)
        return f"Bilgi hafızaya kaydedildi (ID: {point_id[:8]}...)"
    except Exception as exc:
        logger.error("remember_error", error=str(exc))
        return f"Hafızaya kaydetme başarısız: {exc}"


@mcp.tool()
async def search_long_term_memory(
    query: str,
    top_k: int = 5,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """
    Jarvis'in hafızasından bilgi ara.

    Semantik benzerlik kullanarak ilgili bilgileri getirir.

    Args:
        query: Arama sorgusu
        top_k: Maksimum sonuç sayısı (varsayılan: 5)
        category: Filtre: belirli bir kategoriyle sınırla (opsiyonel)

    Returns:
        Bulunan hafıza kayıtları listesi
    """
    if _qdrant_memory is None:
        return [{"error": "Hafıza sistemi henüz başlatılmadı."}]

    try:
        results = await _qdrant_memory.search(
            query=query,
            top_k=top_k,
            category=category,
        )

        return [
            {
                "text": r.text,
                "score": round(r.score, 3),
                "category": r.category,
                "timestamp": r.timestamp,
            }
            for r in results
        ]
    except Exception as exc:
        logger.error("recall_error", error=str(exc))
        return [{"error": f"Hafıza araması başarısız: {exc}"}]
