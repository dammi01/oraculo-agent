# 🔮 Oráculo

Agente de IA que responde perguntas sobre a **Oracle Cloud Infrastructure (OCI)**, com base em documentação oficial da Oracle (Always Free Resources, Compute Shapes, Security Lists e Security Rules).

Projeto desenvolvido para o **Challenge Alura Agente**, parte da trilha **Oracle Next Education (ONE)**, em colaboração com a **Alura**.

---

## 📖 Sobre o projeto

O Oráculo é um agente conversacional do tipo RAG (*Retrieval-Augmented Generation*): ele lê uma base de conhecimento em PDF, transforma o conteúdo em embeddings, e usa um LLM para responder perguntas em linguagem natural — **apenas com base no que está documentado**, recusando-se a responder quando a informação não está na base (evitando alucinação).

## 🏗️ Arquitetura da solução

```
PDF (base de conhecimento)
        │
        ▼
   loader.py  ──► extração de texto (pdfplumber)
        │
        ▼
  embedder.py ──► chunking + embeddings multilíngues
        │
        ▼
   index.pkl  ──► índice vetorial local
        │
        ▼
   agent.py   ──► busca por similaridade + geração de resposta (Gemini 3.1 Flash-Lite)
        │
        ▼
     app.py   ──► interface web (Streamlit)
```

**Fluxo resumido:** o usuário faz uma pergunta na interface → o agente busca os trechos mais relevantes da base de conhecimento → o LLM gera uma resposta em português, fundamentada apenas nesses trechos.

## 🛠️ Tecnologias e ferramentas

- **Python** (gerenciamento de dependências com `uv`)
- **pdfplumber** — extração de texto dos PDFs
- **Embeddings multilíngues** — indexação semântica do conteúdo
- **Google Gemini 3.1 Flash-Lite** — geração das respostas
- **Streamlit** — interface web
- **Docker** — containerização para deploy
- **Oracle Cloud Infrastructure (OCI)** — hospedagem/deploy da aplicação

## 📁 Estrutura do repositório

```
oraculo-agent/
├── docs/
│   ├── PRD.md          # requisitos do produto
│   ├── SDD.md          # design técnico da solução
│   └── ADR.md           # log de decisões técnicas e justificativas
├── data/kb/             # base de conhecimento (PDFs)
├── src/
│   ├── ingestion/        # loader.py, embedder.py
│   ├── agent/            # agent.py
│   └── app/               # interface Streamlit + assets (logos)
├── scripts/
│   └── build_index.py     # gera/atualiza o índice vetorial
├── main.py
├── Dockerfile
└── pyproject.toml
```

## ▶️ Como executar o projeto

### Pré-requisitos
- Python 3.x
- [uv](https://github.com/astral-sh/uv) instalado
- Uma `GOOGLE_API_KEY` válida (Gemini API)

### Passos

```bash
# 1. Clonar o repositório
git clone https://github.com/dammi01/oraculo-agent.git
cd oraculo-agent

# 2. Instalar dependências
uv sync

# 3. Configurar variável de ambiente
export GOOGLE_API_KEY="sua_chave_aqui"

# 4. Gerar o índice vetorial (a partir dos PDFs em data/kb/)
uv run scripts/build_index.py

# 5. Rodar a aplicação
uv run streamlit run src/app/main.py
```

A aplicação abrirá localmente em `http://localhost:8501`.

## ☁️ Deploy na OCI

> **[Preencher após o deploy]**
> - Link público da aplicação:
> - Print da aplicação em execução:

## 💬 Exemplos de perguntas que o agente responde

> **[Ajustar com perguntas reais testadas — sugestões abaixo com base na base de conhecimento atual]**

- "O que está incluído no Always Free Tier da OCI?"
- "Quais são os shapes de Compute disponíveis gratuitamente?"
- "Como funcionam as Security Lists na OCI?"
- "Qual a diferença entre Security Lists e Security Rules?"

## 🤖 Exemplos de respostas geradas

> **[Colar aqui 2–3 pares pergunta/resposta reais capturados do agente rodando, com prints ou texto copiado]**

---

*Desenvolvido por [Michael](https://github.com/dammi01) — Challenge Alura Agente / Oracle Next Education.*
