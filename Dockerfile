# Dockerfile para deploy da API YOLO
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY src/ ./src/
COPY app.yaml .

# Cria diretório para o modelo
RUN mkdir -p /app/models

# Define variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expõe a porta
EXPOSE 8080

# Define o comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "src.main:app"]
