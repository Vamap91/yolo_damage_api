#!/bin/bash

# Script de deploy para Google Cloud App Engine
# Execute este script após configurar o gcloud CLI

echo "🚀 Iniciando deploy da API YOLO para Google Cloud..."

# Verifica se o gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI não encontrado. Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verifica se está autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Não está autenticado no Google Cloud. Execute: gcloud auth login"
    exit 1
fi

# Verifica se o projeto está configurado
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Projeto não configurado. Execute: gcloud config set project SEU_PROJECT_ID"
    exit 1
fi

echo "📋 Projeto configurado: $PROJECT_ID"

# Habilita as APIs necessárias
echo "🔧 Habilitando APIs necessárias..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Cria o app se não existir
echo "🏗️ Verificando/criando App Engine..."
if ! gcloud app describe &> /dev/null; then
    echo "Criando nova aplicação App Engine..."
    echo "Escolha uma região (ex: us-central1, southamerica-east1):"
    gcloud app create
fi

# Faz o deploy
echo "🚀 Fazendo deploy da aplicação..."
gcloud app deploy app.yaml --quiet

# Obtém a URL da aplicação
APP_URL=$(gcloud app describe --format="value(defaultHostname)")
echo ""
echo "✅ Deploy concluído com sucesso!"
echo "🌐 URL da aplicação: https://$APP_URL"
echo "📚 Documentação da API: https://$APP_URL"
echo "🔍 Health check: https://$APP_URL/api/damage/health"
echo ""
echo "📝 Para visualizar logs: gcloud app logs tail -s default"
echo "📊 Para monitorar: gcloud app browse"
