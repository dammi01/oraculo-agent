"""scripts/build_index.py

Reconstrói data/kb/index.pkl. Existe como script separado (em vez de
rodar embedder.py direto) porque o Python sempre marca o módulo
executado como entrypoint como "__main__" — mesmo com `python -m` —
e o pickle grava a classe Chunk com esse nome de módulo. Rodando o
build a partir daqui, `embedder.py` é importado normalmente, então
Chunk fica registrada como `src.ingestion.embedder.Chunk`, que é o
caminho que o resto do projeto (agent.py, app.py) espera ao
descompactar o pickle.

Uso, a partir da raiz do projeto:
    uv run python scripts/build_index.py
"""

import sys
from pathlib import Path

# Garante que a raiz do projeto está no sys.path, já que rodar este
# script direto só adiciona a pasta scripts/ ao path, não a raiz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.embedder import build_index

if __name__ == "__main__":
    chunks = build_index()
    print(f"{len(chunks)} chunks indexados e salvos em data/kb/index.pkl")
