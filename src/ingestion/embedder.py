"""src/ingestion/embedder.py

Divide as páginas carregadas em chunks menores, gera embeddings
multilíngues (PT-BR <-> EN) e persiste um índice simples em disco
para a etapa de retrieval do agente.
"""

import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from src.ingestion.loader import DocumentPage, load_knowledge_base

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # retrieval PT<->EN
INDEX_PATH = Path("data/kb/index.pkl")

CHUNK_SIZE = 800     # caracteres por chunk — cabe bem no contexto do LLM
CHUNK_OVERLAP = 150  # evita cortar uma frase relevante bem na fronteira


@dataclass
class Chunk:
    source: str
    page_number: int
    text: str
    embedding: np.ndarray = field(default=None, repr=False)


def chunk_pages(pages: list[DocumentPage], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Quebra cada página em chunks com sobreposição, respeitando fronteiras de parágrafo quando possível."""
    chunks = []
    for page in pages:
        paragraphs = [p.strip() for p in page.text.split("\n") if p.strip()]
        buffer = ""
        for para in paragraphs:
            if len(buffer) + len(para) <= size:
                buffer += (" " if buffer else "") + para
            else:
                if buffer:
                    chunks.append(Chunk(source=page.source, page_number=page.page_number, text=buffer))
                # inicia o próximo buffer já com overlap do fim do anterior
                buffer = buffer[-overlap:] + " " + para if buffer else para
        if buffer:
            chunks.append(Chunk(source=page.source, page_number=page.page_number, text=buffer))
    return chunks


def embed_chunks(chunks: list[Chunk], model: SentenceTransformer) -> list[Chunk]:
    """Gera o embedding de cada chunk, in-place."""
    texts = [c.text for c in chunks]
    vectors = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    for chunk, vector in zip(chunks, vectors):
        chunk.embedding = vector
    return chunks


def save_index(chunks: list[Chunk], path: Path = INDEX_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(chunks, f)


def load_index(path: Path = INDEX_PATH) -> list[Chunk]:
    with open(path, "rb") as f:
        return pickle.load(f)


def build_index() -> list[Chunk]:
    """Pipeline completo: carrega PDFs -> chunking -> embeddings -> salva."""
    pages = load_knowledge_base()
    chunks = chunk_pages(pages)
    model = SentenceTransformer(EMBEDDING_MODEL)
    chunks = embed_chunks(chunks, model)
    save_index(chunks)
    return chunks


if __name__ == "__main__":
    chunks = build_index()
    print(f"{len(chunks)} chunks indexados e salvos em {INDEX_PATH}")
    print(f"Exemplo — {chunks[0].source} (pág. {chunks[0].page_number}): {chunks[0].text[:150]}")
    print(f"Dimensão do embedding: {chunks[0].embedding.shape}")
