"""src/ingestion/loader.py

Lê os PDFs da base de conhecimento e extrai texto por página,
mantendo metadados de origem (arquivo + página) para citação
posterior nas respostas do agente.
"""

from dataclasses import dataclass
from pathlib import Path

import pdfplumber

KB_DIR = Path("data/kb")


@dataclass
class DocumentPage:
    source: str       # nome do arquivo PDF
    page_number: int  # 1-indexed, mais legível pro usuário
    text: str


def load_pdf(path: Path) -> list[DocumentPage]:
    """Extrai o texto de cada página de um único PDF."""
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:  # ignora páginas em branco (capa, etc.)
                pages.append(DocumentPage(source=path.name, page_number=i, text=text))
    return pages


def load_knowledge_base(kb_dir: Path = KB_DIR) -> list[DocumentPage]:
    """Carrega todos os PDFs do diretório da base de conhecimento."""
    pdf_files = sorted(kb_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {kb_dir}")

    all_pages = []
    for pdf_path in pdf_files:
        all_pages.extend(load_pdf(pdf_path))

    return all_pages


if __name__ == "__main__":
    pages = load_knowledge_base()
    print(f"{len(pages)} páginas carregadas de {len(set(p.source for p in pages))} documento(s)")
    print(f"Exemplo — {pages[0].source}, pág. {pages[0].page_number}:")
    print(pages[0].text[:200])
