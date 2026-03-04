"""
Jarvis AI — Qdrant Vektörel Hafıza

Jarvis'in uzun vadeli hafızası. Konuşmalar, önemli bilgiler ve
bağlam verileri embedding vektörleri olarak Qdrant'ta saklanır.

Embedding: Ollama nomic-embed-text (768 boyut)
Sunucu: Ubuntu (Tailscale mesh — 100.x.x.x:6333)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

import ollama as ollama_sync
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from logging_config import get_logger
from settings import JarvisSettings, get_settings

logger = get_logger("integrations.qdrant")


@dataclass
class MemoryResult:
    """Qdrant arama sonucu."""

    text: str
    score: float
    category: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


class QdrantMemory:
    """
    Jarvis'in uzun vadeli vektörel hafızası.

    Kullanım:
        memory = QdrantMemory(settings)
        await memory.connect()
        await memory.store("Kullanıcı Python öğrenmek istiyor", category="preference")
        results = await memory.search("Python hakkında ne biliyoruz?")
        await memory.close()
    """

    def __init__(self, settings: JarvisSettings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: AsyncQdrantClient | None = None
        self._ollama = ollama_sync.AsyncClient(host=self._settings.ollama_base_url)
        self._collection = self._settings.qdrant_collection
        self._embedding_model = self._settings.embedding_model
        self._embedding_dim = self._settings.embedding_dim

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def connect(self) -> None:
        """
        Qdrant'a bağlan ve collection'ı bootstrap et.
        Collection yoksa otomatik oluşturur.
        """
        self._client = AsyncQdrantClient(
            url=self._settings.qdrant_url,
            timeout=self._settings.qdrant_timeout,
        )

        # Collection var mı kontrol et
        collections = await self._client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self._collection not in collection_names:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=self._embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                "collection_created",
                name=self._collection,
                dim=self._embedding_dim,
            )
        else:
            logger.info("collection_exists", name=self._collection)

    async def _embed(self, text: str) -> list[float]:
        """Metni Ollama embedding modeli ile vektöre dönüştür."""
        response = await self._ollama.embed(
            model=self._embedding_model,
            input=text,
        )
        return response["embeddings"][0]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    async def store(
        self,
        text: str,
        category: str = "general",
        metadata: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> str:
        """
        Metni embed edip Qdrant'a kaydet.

        Args:
            text: Kaydedilecek metin
            category: Kategori (general, preference, fact, conversation)
            metadata: Ek metadata
            user_id: Kullanıcı tanımlayıcısı

        Returns:
            Oluşturulan point ID'si
        """
        if not self._client:
            raise RuntimeError("Qdrant bağlantısı kurulmamış. connect() çağırın.")

        vector = await self._embed(text)
        point_id = str(uuid4())

        payload: dict[str, Any] = {
            "text": text,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id or "system",
            **(metadata or {}),
        }

        await self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

        logger.info(
            "memory_stored",
            point_id=point_id,
            category=category,
            text_length=len(text),
        )
        return point_id

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    async def search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
        user_id: str | None = None,
        score_threshold: float = 0.5,
    ) -> list[MemoryResult]:
        """
        Semantik benzerlik araması.

        Args:
            query: Arama sorgusu
            top_k: Döndürülecek maksimum sonuç sayısı
            category: Filtre: belirli bir kategoriyle sınırla
            user_id: Filtre: belirli bir kullanıcıyla sınırla
            score_threshold: Minimum benzerlik skoru

        Returns:
            Sıralanmış MemoryResult listesi
        """
        if not self._client:
            raise RuntimeError("Qdrant bağlantısı kurulmamış. connect() çağırın.")

        query_vector = await self._embed(query)

        # Filtre oluştur
        conditions = []
        if category:
            conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
            )
        if user_id:
            conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )

        query_filter = Filter(must=conditions) if conditions else None

        results = await self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=score_threshold,
        )

        return [
            MemoryResult(
                text=point.payload.get("text", ""),
                score=point.score,
                category=point.payload.get("category", "general"),
                timestamp=point.payload.get("timestamp", ""),
                metadata={
                    k: v
                    for k, v in point.payload.items()
                    if k not in ("text", "category", "timestamp")
                },
            )
            for point in results.points
        ]

    async def close(self) -> None:
        """Bağlantıyı kapat."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("qdrant_disconnected")
