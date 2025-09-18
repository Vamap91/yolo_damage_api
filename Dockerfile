# Dockerfile corrigido para Google Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Instala apenas dependências essenciais que funcionam no Cloud Run
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements.txt primeiro (para cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY src/ ./src/

# Define variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=8080

# Expõe a porta que Cloud Run espera
EXPOSE 8080

# Comando de inicialização para Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 src.main:app
