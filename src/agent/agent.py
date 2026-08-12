"""src/agent/agent.py

Classe principal do Oráculo: faz retrieval por similaridade de cosseno
sobre o índice de chunks gerado pelo embedder e usa o Gemini para
gerar a resposta final, sempre em português, mesmo que o contexto
recuperado esteja em inglês.
"""

import os
from dataclasses import dataclass

import numpy as np
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

from src.ingestion.embedder import EMBEDDING_MODEL, Chunk, load_index

TOP_K = 4  # quantos chunks recuperar por pergunta

SYSTEM_PROMPT = """Você é o Oráculo, um assistente que responde perguntas sobre \
documentação técnica da Oracle Cloud Infrastructure (OCI).

O contexto abaixo pode estar em inglês. Você DEVE:
- Responder SEMPRE em português do Brasil, independente do idioma do contexto.
- Usar linguagem simples e direta, evitando jargão técnico desnecessário.
- Basear a resposta apenas no contexto fornecido; se não houver informação \
suficiente, diga isso claramente em vez de inventar.

Contexto:
{context}

Pergunta: {question}
"""


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


class OraculoAgent:
    def __init__(self, model_name: str = "gemini-3.1-flash-lite"):
        load_dotenv()
        if not os.getenv("GOOGLE_API_KEY"):
            raise RuntimeError("GOOGLE_API_KEY não encontrada — confira o .env")

        self.client = genai.Client()  # lê GOOGLE_API_KEY do ambiente automaticamente
        self.model_name = model_name
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.chunks: list[Chunk] = load_index()

    def _retrieve(self, question: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
        """Busca por força bruta: similaridade de cosseno via produto escalar
        (os embeddings já foram normalizados na indexação)."""
        query_vector = self.embedder.encode(question, normalize_embeddings=True)
        chunk_vectors = np.array([c.embedding for c in self.chunks])
        scores = chunk_vectors @ query_vector

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [RetrievedChunk(chunk=self.chunks[i], score=float(scores[i])) for i in top_indices]

    def _build_prompt(self, question: str, retrieved: list[RetrievedChunk]) -> str:
        context = "\n\n---\n\n".join(
            f"[Fonte: {r.chunk.source}, pág. {r.chunk.page_number}]\n{r.chunk.text}"
            for r in retrieved
        )
        return SYSTEM_PROMPT.format(context=context, question=question)

    def ask(self, question: str) -> str:
        retrieved = self._retrieve(question)
        prompt = self._build_prompt(question, retrieved)
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text


if __name__ == "__main__":
    agent = OraculoAgent()
    perguntas_teste = [
        "Quantos OCPUs tem o shape Always Free ARM depois do corte de agosto de 2026?",
        "Minha porta 8501 não abre, o que pode estar errado?",
        "Qual a diferença entre regra stateful e stateless?",
    ]
    for pergunta in perguntas_teste:
        print(f"\nP: {pergunta}")
        print(f"R: {agent.ask(pergunta)}")
