# ADR — Oráculo

Registro de decisões técnicas e de produto, com o porquê. Formato inspirado em ADR (Architecture Decision Record): cada entrada é curta, tem o problema, a decisão e a alternativa descartada.

---

### D01 — Domínio da base de conhecimento: documentação da própria OCI
**Contexto:** o challenge sugere domínios genéricos (e-commerce, SaaS, fintech).
**Decisão:** usar a documentação oficial da OCI (Always Free, Compute Shapes, Security Lists/Rules) — projeto meta, coerente com o momento de aprendizado.
**Alternativa descartada:** reaproveitar os dados de telemetria do F1 Agent — descartado porque é dado tabular, não documentação textual tipo política/manual, então RAG sobre ele ficaria artificial pro formato do challenge.

### D02 — Suporte bilíngue PT-BR / EN como requisito de design, não afterthought
**Contexto:** documentos-fonte em inglês, público-alvo pergunta em português.
**Decisão:** tratar isso como requisito desde o PRD, com duas frentes: embedding multilíngue (retrieval) + prompt de sistema fixando resposta em PT-BR simplificado (geração).
**Porquê importa:** retrieval e geração são etapas independentes — resolver só a geração (fácil) sem resolver o retrieval (mais sutil) faz o agente "não achar" a resposta certa mesmo respondendo em português perfeito.

### D03 — Embedding model: `paraphrase-multilingual-MiniLM-L12-v2`
**Contexto:** o F1 Agent usava `all-MiniLM-L6-v2`, majoritariamente treinado em inglês.
**Decisão:** trocar por um modelo multilíngue, que mapeia PT e EN pro mesmo espaço semântico.
**Alternativa considerada:** `intfloat/multilingual-e5-small` — mais forte, um pouco mais pesado; fica como upgrade futuro se o retrieval do MiniLM não for suficiente.

### D04 — Extração de PDF: `pdfplumber`, não `pypdf`
**Contexto:** `pypdf` extraiu texto sem espaços entre palavras nos PDFs gerados via pandoc/xelatex ("OracleCloudInfrastructure—AlwaysFreeResources").
**Decisão:** trocar para `pdfplumber`, que lidou corretamente com o espaçamento.
**Porquê importa:** embeddings gerados sobre texto colado (`OracleCloudInfrastructure` como um token) degradam a qualidade do retrieval — isso foi pego cedo, testando manualmente o texto extraído antes de seguir pro embedder.

### D05 — Vetor store: pickle + numpy (força bruta), sem FAISS
**Contexto:** corpus pequeno (14 páginas, poucas dezenas de chunks).
**Decisão:** busca por similaridade de cosseno por força bruta, índice salvo em pickle.
**Porquê:** FAISS só compensa a partir de milhares de vetores — adicionar agora seria complexidade sem benefício real. Fácil de trocar depois se o corpus crescer.

### D06 — Chunking por parágrafo com overlap (800 caracteres, overlap 150)
**Contexto:** cada `DocumentPage` do loader vem com o texto inteiro da página.
**Decisão:** quebrar respeitando fronteiras de parágrafo, com overlap entre chunks consecutivos.
**Porquê:** overlap evita que uma frase relevante fique cortada exatamente na fronteira entre dois chunks, perdendo sentido isolada em qualquer um dos dois lados.

### D07 — LLM de geração: Gemini 3.1 Flash-Lite
**Contexto:** já havia `GOOGLE_API_KEY` configurado do F1 Agent; múltiplos modelos Gemini disponíveis no free tier.
**Decisão:** Flash-Lite em vez de 3 Flash/3.5 Flash.
**Porquê:** a tarefa (RAG simples — recuperar + responder objetivamente) não exige o poder de raciocínio de um modelo maior; retrieval bem feito importa mais que "inteligência" do gerador. Cota mais generosa no free tier é bônus, não motivo principal.
**Risco assumido:** modelo ainda em preview, cotas podem mudar — documentado conscientemente, não ignorado.

### D08 — Deploy: `VM.Standard.E2.1.Micro` (x86), não `A1.Flex` (ARM)
**Contexto:** Always Free oferece as duas opções; Oracle reduziu a cota do A1.Flex pela metade com enforcement em 18/08/2026 — um dia antes do prazo do challenge.
**Decisão:** usar o shape x86, sem fila de capacidade e sem necessidade de rebuild de imagem Docker multi-arch.
**Nota:** o `A1.Flex` continua sendo a escolha certa para uma VPS pessoal futura (mais RAM/CPU real), só não para este prazo apertado — decisão separada, não descarte definitivo do ARM.

### D09 — Estrutura do repositório: `docs/` para PRD/SDD, não root
**Contexto:** rubric do challenge avalia organização do repositório.
**Decisão:** `docs/PRD.md`, `docs/SDD.md`, `README.md` no root linkando pra eles.

### D10 — Gerenciamento de projeto: `uv` + `pyproject.toml`
**Decisão:** `uv` como instalador/gerenciador de venv, `pyproject.toml` como fonte única de dependências, `uv.lock` para reprodutibilidade.
**Alternativa descartada:** `requirements.txt` — sem motivo pra usar num projeto novo hoje.
