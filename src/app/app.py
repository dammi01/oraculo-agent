"""src/app/app.py

UI do Oráculo em Streamlit — tema light, estilo Oracle: fundo
branco, tipografia limpa, vermelho da marca só em destaques
pontuais. Cabeçalho com espaço para os logos oficiais (Oracle,
Oracle Next Education, Alura) e rodapé de colaboração. Fora do
escopo mínimo do PRD, mas o projeto está adiantado então vale
investir aqui.

Os logos NÃO são baixados/embutidos automaticamente (são marcas de
terceiros) — veja src/app/assets/README.md para onde colocá-los.
Sem o arquivo, cai num fallback em texto.
"""

import sys
from pathlib import Path

# Garante que a raiz do projeto está no sys.path, já que o Streamlit
# só adiciona a pasta do próprio script (src/app/), não a raiz.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from src.agent.agent import OraculoAgent

ASSETS_DIR = Path(__file__).parent / "assets"

EXEMPLOS = [
    "Quantos OCPUs tem o shape Always Free ARM?",
    "Qual a diferença entre regra stateful e stateless?",
    "O que é o Free Tier da OCI?",
]

ORACLE_RED = "#C74634"
TEXT_DARK = "#161513"      # cor de texto padrão da HP da Oracle
TEXT_MUTED = "#5c5b57"
BG_LIGHT = "#FFFFFF"
CARD_BG = "#F7F7F5"        # cinza bem claro dos cards da HP da Oracle
BORDER = "#E5E4E1"
LOGO_BADGE_BG = "#161513"  # fundo escuro atrás dos logos claros (ONE/Alura), pra não sumirem no fundo branco

st.set_page_config(page_title="Oráculo · OCI Assistant", page_icon="🔮", layout="centered")

CUSTOM_CSS = f"""
<style>
.stApp {{
    background: {BG_LIGHT};
}}
.oraculo-header {{
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
}}
.oraculo-header h1 {{
    font-size: 2.6rem;
    color: {TEXT_DARK};
    font-weight: 600;
    margin-bottom: 0;
}}
.oraculo-header p {{
    color: {TEXT_MUTED};
    font-size: 1rem;
}}
.logo-row {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 0 1.2rem 0;
}}
.logo-badge {{
    background: {LOGO_BADGE_BG};
    border-radius: 8px;
    padding: 0.45rem 0.9rem;
    display: inline-flex;
    align-items: center;
    line-height: 1;
}}
.logo-badge img {{
    max-height: 26px;
    display: block;
}}
.logo-fallback {{
    font-weight: 600;
    color: #ffffff;
    font-size: 0.9rem;
    letter-spacing: 0.03em;
}}
.oracle-wordmark {{
    font-weight: 800;
    color: {ORACLE_RED};
    font-size: 1.4rem;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    font-family: Arial, Helvetica, sans-serif;
}}
.answer-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 3px solid {ORACLE_RED};
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
    color: {TEXT_DARK};
}}
.collab-footer {{
    text-align: center;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid {BORDER};
    color: {TEXT_MUTED};
    font-size: 0.8rem;
}}
.collab-footer img {{
    max-height: 18px;
    vertical-align: middle;
}}
div.stButton > button[kind="primary"] {{
    background-color: {ORACLE_RED};
    border-color: {ORACLE_RED};
}}
div.stButton > button[kind="primary"]:hover {{
    background-color: #a83a29;
    border-color: #a83a29;
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _logo_html(filename: str, alt: str) -> str:
    """Retorna um <img> dentro de um badge escuro (pra funcionar mesmo com
    logos brancos/claros em fundo branco). Se o arquivo não existir, cai
    num fallback em texto dentro do mesmo badge."""
    path = ASSETS_DIR / filename
    if path.exists():
        import base64

        encoded = base64.b64encode(path.read_bytes()).decode()
        ext = path.suffix.lstrip(".")
        inner = f'<img src="data:image/{ext};base64,{encoded}" alt="{alt}" />'
    else:
        inner = f'<span class="logo-fallback">{alt}</span>'
    return f'<span class="logo-badge">{inner}</span>'


def _oracle_wordmark() -> str:
    """Não temos o logo oficial da Oracle (protegido contra download no
    site) — recriamos só a referência tipográfica: bold, vermelho,
    maiúsculo. Não é uma cópia do logotipo, só uma alusão a ele."""
    return '<span class="oracle-wordmark">ORACLE</span>'


def render_header() -> None:
    st.markdown(
        """
        <div class="oraculo-header">
            <h1>🔮 Oráculo</h1>
            <p>Seu assistente para dúvidas sobre a documentação da OCI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="logo-row">
            {_oracle_wordmark()}
            {_logo_html("one_logo.png", "Oracle Next Education")}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        f"""
        <div class="collab-footer">
            Em colaboração com {_logo_html("alura_logo.png", "Alura")}
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner="Carregando o Oráculo...")
def get_agent() -> OraculoAgent:
    return OraculoAgent()


def main() -> None:
    render_header()

    with st.sidebar:
        st.subheader("💡 Exemplos de perguntas")
        for exemplo in EXEMPLOS:
            if st.button(exemplo, use_container_width=True):
                st.session_state["pergunta"] = exemplo
        st.divider()
        st.caption("Respostas geradas a partir da documentação oficial da OCI, sempre em PT-BR.")

    try:
        agent = get_agent()
    except RuntimeError as e:
        st.error(f"Erro ao iniciar o Oráculo: {e}")
        st.stop()

    pergunta = st.text_input(
        "Sua pergunta",
        key="pergunta",
        placeholder="Ex.: O que é o Free Tier da OCI?",
        label_visibility="collapsed",
    )

    if st.button("🔮 Perguntar", type="primary") and pergunta.strip():
        with st.spinner("Consultando a documentação..."):
            resposta = agent.ask(pergunta)
        st.markdown(f'<div class="answer-card">{resposta}</div>', unsafe_allow_html=True)

    render_footer()


if __name__ == "__main__":
    main()
