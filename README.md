# 🚗 API de Detecção de Danos Veiculares com YOLOv8

Esta é uma API RESTful construída com Flask que utiliza um modelo de Inteligência Artificial (YOLOv8) para detectar, classificar e analisar danos em veículos a partir de imagens. A API foi projetada para ser robusta, escalável e pronta para deploy no Google Cloud Platform (App Engine).

## ✨ Funcionalidades Principais

- **Endpoints RESTful**: Interface clara e bem definida para interagir com o modelo de IA.
- **Detecção Precisa de Danos**: Utiliza o modelo `car_damage_best.pt` para identificar 6 tipos de danos (amassados, riscos, rachaduras, vidros quebrados, faróis/lanternas quebradas, pneus vazios).
- **Análise Detalhada**: Para cada dano, a API retorna severidade, localização e custo estimado de reparo.
- **Processamento Flexível**: Aceita imagens via upload de arquivo (`multipart/form-data`) ou em formato base64 (`application/json`).
- **Análise em Lote**: Endpoint para processar múltiplas imagens em uma única requisição.
- **Página de Demonstração**: Interface web interativa para testar a API diretamente pelo navegador.
- **Pronta para a Nuvem**: Configurada para deploy fácil no Google Cloud App Engine com `app.yaml` e `Dockerfile` inclusos.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.11, Flask, Gunicorn
- **Inteligência Artificial**: Ultralytics YOLOv8, PyTorch
- **Processamento de Imagem**: OpenCV, Pillow
- **Deploy**: Google Cloud App Engine, Docker

## 🚀 Como Executar Localmente

Siga os passos abaixo para rodar a API em seu ambiente de desenvolvimento.

### 1. Pré-requisitos

- Python 3.11 ou superior
- `pip` (gerenciador de pacotes)
- (Opcional) `git` para controle de versão

### 2. Clone o Repositório

Se você estiver usando Git, clone o repositório. Caso contrário, apenas descompacte o arquivo ZIP em um diretório de sua escolha.

```bash
# (Opcional) Se você for clonar de um repositório Git
git clone <URL_DO_SEU_REPOSITORIO>
cd yolo_damage_api
```

### 3. Crie e Ative um Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

### 4. Instale as Dependências

Instale todas as bibliotecas necessárias a partir do arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Execute a Aplicação

Inicie o servidor de desenvolvimento do Flask. O modelo YOLOv8 será baixado automaticamente na primeira execução.

```bash
python src/main.py
```

A API estará disponível em `http://localhost:5000`. Abra este endereço no seu navegador para ver a página de documentação e demonstração.

## 📚 Endpoints da API

A base da URL para todos os endpoints é `/api/damage`.

| Método | Endpoint             | Descrição                                               |
|--------|----------------------|-----------------------------------------------------------|
| `GET`  | `/health`            | Verifica o status da API e do modelo.                     |
| `POST` | `/detect`            | Analisa uma única imagem para detectar danos.             |
| `POST` | `/analyze-batch`     | Analisa um lote de imagens (máximo de 10).                |
| `GET`  | `/model-info`        | Retorna informações sobre o modelo de IA carregado.       |

### Exemplo de Requisição (`/detect` com cURL)

**Usando um arquivo de imagem:**
```bash
curl -X POST -F "image=@caminho/para/sua/imagem.jpg" http://localhost:5000/api/damage/detect
```

**Usando JSON com imagem em base64:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"image_base64": "<sua_string_base64>"}' \
     http://localhost:5000/api/damage/detect
```

## ☁️ Deploy no Google Cloud App Engine

O projeto está pronto para ser implantado no Google Cloud App Engine. Siga os passos abaixo.

### 1. Pré-requisitos de Deploy

- **Conta no Google Cloud**: Com um projeto criado e faturamento ativado.
- **Google Cloud CLI**: Instalado e configurado. [Instruções de instalação](https://cloud.google.com/sdk/docs/install).

### 2. Configure o `gcloud`

Autentique-se e configure o projeto que você deseja usar.

```bash
# Autenticação
gcloud auth login

# Listar projetos
gcloud projects list

# Configurar o projeto
gcloud config set project SEU_PROJECT_ID
```

### 3. Execute o Script de Deploy

O projeto inclui um script `deploy.sh` que automatiza o processo de deploy. Ele habilitará as APIs necessárias, criará o aplicativo App Engine (se for a primeira vez) e implantará o código.

No seu terminal (macOS/Linux), execute:

```bash
chmod +x deploy.sh
./deploy.sh
```

O script cuidará de todo o processo. Ao final, ele exibirá a URL da sua API em produção.

## 📦 Estrutura do Projeto

```
/yolo_damage_api
│
├── venv/                    # Ambiente virtual (ignorado pelo Git)
├── src/
│   ├── models/              # Modelos de banco de dados (exemplo)
│   ├── routes/
│   │   ├── damage_detection.py # Lógica dos endpoints da API
│   │   └── user.py             # Exemplo de rotas de usuário
│   ├── services/
│   │   └── yolo_service.py     # Serviço principal de detecção com YOLO
│   ├── static/
│   │   └── index.html          # Página de demonstração e documentação
│   └── main.py              # Ponto de entrada da aplicação Flask
│
├── app.yaml                 # Configuração para Google Cloud App Engine
├── Dockerfile               # Configuração para containerização com Docker
├── requirements.txt         # Dependências Python
├── deploy.sh                # Script de deploy para Google Cloud
├── .gcloudignore            # Arquivos a serem ignorados pelo gcloud
├── .gitignore               # Arquivos a serem ignorados pelo Git
└── README.md                # Esta documentação
```

---

*Este projeto foi desenvolvido para fornecer uma solução de API robusta e escalável para a detecção de danos veiculares, pronta para integração com sistemas externos como o Lovable e para deploy em ambientes de nuvem.*

