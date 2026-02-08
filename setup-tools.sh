#!/bin/bash
# Setup de ferramentas para todos os agentes do Dunder Mifflin
# Execute como: ./setup-tools.sh

set -e

echo "🚀 Dunder Mifflin - Setup de Ferramentas"
echo "=========================================="
echo ""

# Verifica se está rodando como root (não recomendado)
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Não rode este script como root/sudo"
   exit 1
fi

# Verifica dependências básicas
echo "📋 Verificando dependências básicas..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale primeiro: https://nodejs.org"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale primeiro."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git não encontrado. Instale primeiro."
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ Python: $(python3 --version)"
echo "✅ Git: $(git --version)"
echo ""

# Cria pasta de binários local
mkdir -p ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

echo "📦 Instalando ferramentas Node.js globais..."
echo "--------------------------------------------"

# Performance & QA
npm install -g lighthouse lighthouse-ci @sitespeed.io/sitespeed.io 2>/dev/null || echo "⚠️  Alguns pacotes podem ter falhado"
npm install -g depcheck ts-prune 2>/dev/null || true
npm install -g pa11y @mermaid-js/mermaid-cli 2>/dev/null || true

# Testes
npm install -g jest @playwright/test newman 2>/dev/null || true

# Deploy & Dev
npm install -g vercel netlify-cli ngrok 2>/dev/null || true

# Outros
npm install -g write-good @faker-js/faker 2>/dev/null || true
npm install -g @openapitools/openapi-generator-cli 2>/dev/null || true

echo "✅ Node.js tools instaladas"
echo ""

echo "🐍 Instalando ferramentas Python..."
echo "-----------------------------------"

# Segurança & Qualidade
pip3 install --user semgrep unimport black ruff pytest 2>/dev/null || true

# AI & Data
pip3 install --user openai langchain 2>/dev/null || true

# Utilitários
pip3 install --user vale httpie factory_boy 2>/dev/null || true

echo "✅ Python tools instaladas"
echo ""

echo "🐳 Verificando Docker..."
echo "------------------------"

if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
    
    # Pull de imagens úteis
    echo "📥 Baixando imagens Docker..."
    docker pull zricethezav/gitleaks 2>/dev/null || echo "⚠️  gitleaks - tentar manualmente"
    docker pull aquasec/trivy 2>/dev/null || echo "⚠️  trivy - tentar manualmente"
else
    echo "⚠️  Docker não encontrado. Instale: https://docs.docker.com/get-docker/"
fi

echo ""

echo "☸️  Verificando Kubernetes tools..."
echo "-----------------------------------"

if ! command -v kubectl &> /dev/null; then
    echo "📥 Instalando kubectl..."
    curl -LO "https://dl.k8s/release/$(curl -L -s https://dl.k8s/release/stable.txt)/bin/linux/amd64/kubectl" 2>/dev/null
    chmod +x kubectl
    mv kubectl ~/.local/bin/ 2>/dev/null || echo "⚠️  kubectl - tentar manualmente"
fi

echo ""

echo "⚡ Instalando k6..."
echo "------------------"

if ! command -v k6 &> /dev/null; then
    echo "📥 Baixando k6..."
    curl -fsSL https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz | tar -xzf - -C /tmp
    mv /tmp/k6-v0.47.0-linux-amd64/k6 ~/.local/bin/ 2>/dev/null || echo "⚠️  k6 - tentar manualmente"
fi

echo ""

echo "☁️  Verificando Cloud CLIs..."
echo "-----------------------------"

# AWS CLI
if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI não encontrado. Instale: https://aws.amazon.com/cli/"
else
    echo "✅ AWS CLI: $(aws --version)"
fi

# GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "📥 Instalando GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null || echo "⚠️  gh - tentar manualmente"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null 2>/dev/null || true
    sudo apt update && sudo apt install gh -y 2>/dev/null || echo "⚠️  gh - instalar manualmente"
else
    echo "✅ GitHub CLI: $(gh --version | head -1)"
fi

echo ""

echo "🔧 Configuração de ambiente..."
echo "------------------------------"

# Adiciona ~/.local/bin ao PATH se não estiver
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ PATH atualizado no .bashrc"
fi

# Verifica se GITHUB_TOKEN está configurado
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN não configurado"
    echo "   Configure com: export GITHUB_TOKEN='seu_token_aqui'"
    echo "   Adicione ao ~/.bashrc para persistir"
else
    echo "✅ GITHUB_TOKEN configurado"
fi

echo ""
echo "=========================================="
echo "✅ Setup completo!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Reinicie o terminal ou rode: source ~/.bashrc"
echo "   2. Configure GITHUB_TOKEN se ainda não configurou"
echo "   3. Teste as ferramentas: lighthouse --version"
echo ""
echo "📖 Veja o guia completo em: docs/AGENTS_TOOLS.md"
echo ""
