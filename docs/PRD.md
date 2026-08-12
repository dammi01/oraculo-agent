# PRD — Oráculo

**Repositório:** `oraculo-agent`
**Contexto:** Challenge Alura Agente (Oracle ONE / Oracle + Alura)
**Prazo de entrega:** 19 de agosto de 2026

---

## 1. Problema

Empresas acumulam documentação interna (manuais, políticas, guias técnicos) que ninguém lê até precisar dela sob pressão — e aí gastam tempo procurando manualmente. O desafio pede um agente de IA que responda perguntas em linguagem natural sobre esses documentos.

**Recorte deste projeto:** em vez de um domínio genérico de e-commerce/FAQ (como sugerido pelos exemplos do curso), o Oráculo responde perguntas sobre a **própria documentação oficial da OCI** (Always Free Resources, Compute Shapes, Security Lists e Security Rules). É meta — um agente que ajuda quem está aprendendo OCI a não se perder na doc oficial, incluindo o autor deste projeto.

## 2. Diferenciais deste projeto

1. **Domínio meta e coerente com o momento de aprendizado** — não é um FAQ genérico da lista de sugestões do curso.
2. **RAG bilíngue de verdade (PT-BR ↔ EN):** os documentos-fonte estão em inglês; o público-alvo (alunos do curso) faz perguntas e espera respostas em português. Isso é tratado como requisito de design, não como detalhe de tradução — ver seção 5.
3. **Reaproveitamento de arquitetura validada** no [[llm-zoomcamp]] (F1 Agent) — reduz risco de execução no prazo apertado.

## 3. Público-alvo

Alunos e colegas de curso (ONE/Alura) que precisam entender rapidamente limites, shapes e regras de rede da OCI durante o próprio challenge — sem fluência técnica plena em inglês nem, necessariamente, domínio de leitura técnica avançada em português.

## 4. Escopo funcional (requisitos do challenge)

| # | Requisito (do desafio oficial) | Como o Oráculo atende |
|---|---|---|
| 1 | Ler e processar documento(s) PDF/CSV | Dois PDFs consolidados a partir da doc oficial da OCI (ver [[oci-alura-agente]]) |
| 2 | Responder perguntas em linguagem natural | Agente RAG: retrieval + LLM generativo |
| 3 | Deploy funcional na OCI | VM `VM.Standard.E2.1.Micro` (Always Free, x86), container Docker |
| 4 | Repositório GitHub organizado, com histórico de commits | `oraculo-agent`, commits incrementais desde o início (não squash final) |
| 5 | README completo | Arquitetura, tecnologias, instruções de execução, exemplos de Q&A, evidência de deploy |
| 6 | Evidência do deploy | Link público da app **e** print de funcionamento |

## 5. Requisito de design: suporte bilíngue PT-BR / EN

- **Retrieval:** troca do embedding monolíngue (`all-MiniLM-L6-v2`, usado no F1 Agent) por um **multilíngue** (`paraphrase-multilingual-MiniLM-L12-v2` ou `intfloat/multilingual-e5-small`), para que perguntas em PT-BR encontrem corretamente os chunks em EN.
- **Geração:** prompt de sistema fixa a resposta sempre em PT-BR, independentemente do idioma do contexto recuperado, e instrui **simplificação de linguagem** (evitar jargão desnecessário), não apenas tradução literal.
- **Evidência no README:** comparação lado a lado de retrieval com embedding monolíngue vs. multilíngue para 2–3 perguntas em português, documentando a decisão.

## 6. Fora de escopo (não-objetivos)

- Framework de avaliação formal com ground truth (não exigido pelo challenge, ao contrário do Zoomcamp)
- Monitoramento/observabilidade dedicados
- Interface elaborada — o próprio curso recomenda não investir tempo aqui
- Suporte a mais de 2 documentos-fonte na v1 (pode crescer depois, não é bloqueante)

## 7. Critérios de sucesso (mapeados ao rubric do challenge)

- [ ] Agente responde corretamente a perguntas sobre o conteúdo dos 2 PDFs, em português, mesmo com fonte em inglês
- [ ] Aplicação rodando publicamente na OCI (link ou print funcional)
- [ ] Código no GitHub organizado, com histórico de commits real
- [ ] README com arquitetura, stack, instruções de execução e exemplos de Q&A

## 8. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Zero experiência prévia em OCI | Sessão dedicada de "hello world" na VM antes de depender dela (feito) |
| Prazo apertado (peer reviews do Zoomcamp até 17/08) | Trabalho paralelo desde já; deploy é o item mais arriscado, então é atacado primeiro depois do PRD/SDD |
| Retrieval cross-lingual fraco | Embedding multilíngue definido já no PRD, não como ajuste de última hora |
| Capacidade Always Free indisponível | Shape `E2.1.Micro` (x86) escolhido — sem fila de capacidade, ao contrário do `A1.Flex` (ARM) |

## 9. Decisões em aberto (assunções a confirmar)

- **LLM de geração:** assumindo reaproveitar **Gemini** (já usado no F1 Agent, `GOOGLE_API_KEY` configurado) — trocar é trivial se preferir outro provedor. **Confirmar.**
- **Terceiro documento** (Security Lists/Rules) já construído — cabe na v1 ou fica como "v1.1"? Recomendo incluir na v1, o corpus fica mais rico sem custo real de tempo.
