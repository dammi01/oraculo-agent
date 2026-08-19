FROM python:3.14-slim

WORKDIR /app

# Instala uv (gerenciador de dependências do projeto)
RUN pip install --no-cache-dir uv

# Copia os arquivos de definição de dependências primeiro (cache de build)
COPY pyproject.toml uv.lock ./

# Instala as dependências no ambiente do sistema (sem venv, já estamos isolados no container)
RUN uv sync --frozen --no-dev

# Copia o restante do código da aplicação
COPY . .

EXPOSE 8501

# Ativa o ambiente virtual criado pelo uv e roda o Streamlit
ENV PATH="/app/.venv/bin:$PATH"

CMD ["streamlit", "run", "src/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
