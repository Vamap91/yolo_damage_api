# Dockerfile alternativo - versão mais compatível
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências básicas primeiro
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tenta instalar OpenCV dependencies - versão mais compatível
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    || echo "Alguns pacotes podem não estar disponíveis, continuando..."

# Instala OpenGL dependencies - tenta múltiplas opções
RUN apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    || apt-get install -y --no-install-recommends libgl1 \
    || echo "OpenGL libs not available, using headless mode"

# Limpa cache do apt
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .

# Instala dependências Python com timeout maior
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

# Copia código da aplicação
COPY src/ ./src/

# Define variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=8080
ENV OPENCV_HEADLESS=1

# Expõe a porta
EXPOSE 8080

# Comando de inicialização
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --preload src.main:app
