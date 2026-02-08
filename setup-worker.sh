#!/bin/bash
# Setup do Dunder Mifflin Worker no clawd-B450MHP

set -e

WORKER_DIR="$HOME/.openclaw/workspace/projects/dunder-mifflin"
SERVICE_NAME="dunder-mifflin-worker"

echo "🚀 Configurando Dunder Mifflin Worker..."

# Criar diretório de logs
mkdir -p "$WORKER_DIR/logs"

# Instalar dependências Python
echo "📦 Instalando dependências..."
pip3 install requests --user 2>/dev/null || pip install requests --user 2>/dev/null

# Criar arquivo de ambiente
echo "📝 Criando .env.worker..."
cat > "$WORKER_DIR/.env.worker" << EOF
CONVEX_URL=https://cautious-puffin-441.convex.cloud
CONVEX_DEPLOY_KEY=prod:cautious-puffin-441|eyJ2MiI6ImM3ODkyZGY2Mjg5OTRmMjZiODc0M2MwM2NhOGM4MGUwIn0=
KIMI_API_KEY=sk-kimi-MZA5NCavO4haI48FCOaImTbBgzAPWWReAzlA1NMrdBZoW5z6MroUTc19XQ1hQJb4
EOF

# Criar serviço systemd
echo "⚙️  Criando serviço systemd..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Dunder Mifflin Worker
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKER_DIR
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=$WORKER_DIR/.env.worker
ExecStart=/usr/bin/python3 $WORKER_DIR/worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
sudo systemctl daemon-reload

echo ""
echo "✅ Setup concluído!"
echo ""
echo "🎮 Comandos disponíveis:"
echo "  sudo systemctl start $SERVICE_NAME   # Iniciar worker"
echo "  sudo systemctl stop $SERVICE_NAME    # Parar worker"
echo "  sudo systemctl status $SERVICE_NAME  # Ver status"
echo "  sudo journalctl -u $SERVICE_NAME -f  # Ver logs"
echo ""
echo "🌐 Dashboard: https://dunder-mifflin-three.vercel.app"
