from __future__ import annotations

import logging
import os

from ollama import AsyncClient

from apps.automode.app.ports.output.embedding_port import EmbeddingPort

logger = logging.getLogger("apps")

_MODEL = "bge-m3"
_DEFAULT_HOST = "http://localhost:11434"
EMBEDDING_DIM = 1024


class BgeM3EmbeddingClient(EmbeddingPort):
    def __init__(self, model: str = _MODEL, host: str | None = None) -> None:
        self._model = model
        self._client = AsyncClient(host=host or os.getenv("OLLAMA_HOST", _DEFAULT_HOST))

    async def embed(self, text: str) -> list[float]:
        response = await self._client.embed(model=self._model, input=text)
        embedding = list(response.embeddings[0])
        logger.info("[embedding] BGE-M3 임베딩 생성 dim=%d", len(embedding))
        return embedding
