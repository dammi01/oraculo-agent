# SDD — Oráculo

Companion do [PRD.md](./PRD.md). Foco: como construir, não o quê construir.

---

## 1. Arquitetura (visão geral)

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐     ┌────────────┐
│  PDFs (KB)  │ --> │  Ingestão    │ --> │  Vetor Store       │ --> │  Oráculo   │
│ (OCI docs)  │     │ (chunk+embed)│     │ (embeddings PT/EN) │     │  (.ask())  │
└─────────────┘     └──────────────┘     └───────────────────┘     └─────┬──────┘
                                                                          │
                                                            ┌─────────────┴──────────┐
                                                            │  LLM generativo (PT-BR)│
                                                            └─────────────┬──────────┘
                                                                          │
                                                            ┌─────────────┴──────────┐
                                                            │   UI (Streamlit)        │
                                                            └─────────────────────────┘
```

Deploy: container Docker rodando o pipeline completo, hospedado numa VM `VM.Standard.E2.1.Micro` na OCI, porta exposta via Security List.

## 2. Componentes

### 2.1 Ingestão (`src/ingestion/`)

- Leitura dos PDFs com `pypdf` ou `pdfplumber` (ver skill `pdf` — `pdfplumber` preferível se algum PDF tiver tabelas, como o de Compute Shapes).
- Chunking por seção/parágrafo (reaproveitar lógica de `mart_text_cards` do F1 Agent, adaptando de linhas de telemetria para blocos de texto de documentação).
- Metadados por chunk: documento de origem, seção/título — importante para o agente citar a fonte na resposta.

### 2.2 Embeddings (`src/ingestion/embedder.py`)

```python
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # cross-lingual PT<->EN
model = SentenceTransformer(EMBEDDING_MODEL)
```

Mesma decisão de rodar em CPU (sem dependência de GPU), como no F1 Agent — volume de dados é pequeno (2 PDFs, ~14 páginas), então custo de embedding é trivial.

### 2.3 Vetor Store

Reaproveitar a solução já validada no F1 Agent (armazenamento local — confirmar se foi FAISS, sqlite-vec, ou outro, ao portar o código). Sem necessidade de um vetor store gerenciado na nuvem para este volume de dados.

### 2.4 Classe do agente (`src/agent/agent.py`)

Mesmo padrão do `F1Agent`: classe `OraculoAgent`, método `.ask(question: str) -> str`, context manager. Isso preserva a interface que a UI e os testes já conhecem.

```python
class OraculoAgent:
    def __init__(self, kb_path: str, llm_provider: str = "gemini"):
        ...
    def ask(self, question: str) -> str:
        # 1. embed da pergunta (modelo multilíngue)
        # 2. retrieval top-k chunks
        # 3. prompt: contexto (EN) + instrução de resposta em PT-BR simplificado
        # 4. chamada ao LLM
        # 5. retorna resposta
        ...
```

### 2.5 Prompt de geração (ponto crítico do diferencial bilíngue)

```
Você é o Oráculo, um assistente que responde perguntas sobre documentação
técnica da Oracle Cloud Infrastructure (OCI).

O contexto abaixo pode estar em inglês. Você DEVE:
- Responder SEMPRE em português do Brasil, independente do idioma do contexto.
- Usar linguagem simples e direta, evitando jargão técnico desnecessário.
- Basear a resposta apenas no contexto fornecido; se não houver informação
  suficiente, diga isso claramente em vez de inventar.

Contexto:
{context}

Pergunta: {question}
```

### 2.6 UI (`src/app/app.py`)

Streamlit, mínimo necessário (o curso recomenda não investir tempo aqui): campo de pergunta, exibição da resposta, algumas perguntas de exemplo na sidebar. Reaproveitar estrutura do F1 Agent.

## 3. Stack (resumo)

| Camada | Escolha | Motivo |
|---|---|---|
| Linguagem | Python | Já dominado; sugerido pelo curso |
| Leitura de PDF | `pypdf` / `pdfplumber` | Padrão, já usado no ecossistema do skill `pdf` |
| Embeddings | `sentence-transformers` multilíngue | Habilita retrieval PT↔EN — ver PRD §5 |
| LLM | Gemini (assunção — confirmar) | Já configurado no F1 Agent (`GOOGLE_API_KEY`) |
| UI | Streamlit | Reaproveita padrão validado, mínimo esforço |
| Containerização | Docker | Dockerfile do F1 Agent como ponto de partida |
| Deploy | OCI Compute `VM.Standard.E2.1.Micro` | Always Free garantido, x86 evita rebuild ARM |

## 4. Deploy — passo a passo técnico

Ver histórico da conversa em [[oci-alura-agente]] para o checklist completo (compartment → VM → security list → SSH → Docker → `docker run --restart unless-stopped`). Resumo:

1. Compartment dedicado (`alura-agente` ou `oraculo-agent`)
2. VM `VM.Standard.E2.1.Micro`, imagem Ubuntu, chave SSH
3. Security List: ingress TCP porta 8501 (Streamlit) liberada, `0.0.0.0/0`
4. Docker instalado via script oficial
5. Build/pull da imagem + `docker run -d -p 8501:8501 --restart unless-stopped --env-file .env oraculo-agent`
6. Print + link público como evidência no README

## 5. Testes e validação

- **Local primeiro, sempre** (conselho oficial do curso): validar `.ask()` com perguntas manuais antes de qualquer deploy.
- Conjunto mínimo de perguntas de exemplo para o README (em português, cobrindo os dois documentos):
  - "Quantos OCPUs tem o shape Always Free ARM depois do corte de agosto de 2026?"
  - "Minha porta 8501 não abre, o que pode estar errado?"
  - "Qual a diferença entre regra stateful e stateless?"
- Comparação retrieval monolíngue vs. multilíngue (ver PRD §5) documentada com prints ou tabela no README.

## 6. Estrutura do repositório (proposta inicial)

```
oraculo-agent/
├── PRD.md
├── SDD.md
├── README.md
├── Dockerfile
├── src/
│   ├── ingestion/
│   │   ├── loader.py
│   │   └── embedder.py
│   ├── agent/
│   │   └── agent.py
│   └── app/
│       └── app.py
├── data/
│   └── kb/              # os 2 PDFs
├── .env.example
└── requirements.txt (ou pyproject.toml + uv)
```

## 7. Decisões em aberto (mesmas do PRD, aqui pela lente técnica)

- Confirmar provedor de LLM (Gemini vs. alternativa)
- Confirmar se o vetor store do F1 Agent é diretamente portável ou precisa de ajuste para o novo formato de chunk (texto de documentação vs. telemetria)
