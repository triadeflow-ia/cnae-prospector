# CNAE Prospector - Production Dockerfile
FROM python:3.11-slim

# Metadados
LABEL maintainer="alex@cnaeprospector.com"
LABEL version="1.0.0"
LABEL description="CNAE Prospector - B2B Lead Generation Tool"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Criar diretórios
WORKDIR /app
RUN mkdir -p /app/data/exports /app/data/processed /app/data/raw /app/logs
RUN chown -R appuser:appuser /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Ajustar permissões
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Porta da aplicação
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando padrão
CMD ["python", "run_production.py", "--api", "--host", "0.0.0.0", "--port", "8000"]