#!/bin/bash
#
# Setup do Ralph Discord Bridge v5.1
# Configura PM2 + Fila Persistente + Auto-restart
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
echo "📁 Diretório do projeto: $PROJECT_DIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "🚀 Ralph Discord Bridge v5.1 - Setup"
echo "===================================="
echo ""

# 1. Verificar dependências
echo "🔍 Verificando dependências..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3 não encontrado${NC}"
    exit 1
fi

if ! python3 -c "import discord" 2>/dev/null; then
    echo -e "${YELLOW}⚠️ discord.py não instalado. Instalando...${NC}"
    pip3 install discord.py --user
fi

# Verificar se PM2 está instalado
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}⚠️ PM2 não encontrado. Instalando...${NC}"
    
    if command -v npm &> /dev/null; then
        npm install -g pm2
    else
        echo -e "${YELLOW}⚠️ npm não encontrado. Tentando instalar via apt...${NC}"
        sudo apt-get update && sudo apt-get install -y npm
        npm install -g pm2
    fi
fi

echo -e "${GREEN}✅ Dependências OK${NC}"

# 2. Parar instâncias antigas
echo ""
echo "🛑 Parando instâncias antigas..."
pkill -f discord_bridge.py 2>/dev/null || true
pm2 stop ralph-discord-bridge 2>/dev/null || true
pm2 delete ralph-discord-bridge 2>/dev/null || true
sleep 2

# 3. Backup do bridge antigo
echo ""
echo "💾 Fazendo backup do bridge antigo..."
if [ -f "$SCRIPT_DIR/discord_bridge.py" ]; then
    cp "$SCRIPT_DIR/discord_bridge.py" "$SCRIPT_DIR/discord_bridge.py.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✅ Backup criado${NC}"
fi

# 4. Copiar novo bridge
echo ""
echo "📝 Instalando nova versão..."
cp "$SCRIPT_DIR/discord_bridge_v51.py" "$SCRIPT_DIR/discord_bridge.py"
echo -e "${GREEN}✅ Nova versão instalada${NC}"

# 5. Criar tabela de fila persistente
echo ""
echo "🗄️ Configurando banco de dados..."
python3 << EOF
import sqlite3
import os

db_path = "$PROJECT_DIR/dunder_mifflin.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela de mensagens pendentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discord_pending_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_message_id TEXT NOT NULL,
            discord_channel_id TEXT NOT NULL,
            author_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            retry_count INTEGER DEFAULT 0,
            error TEXT
        )
    """)
    
    # Criar índices
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pending_processed 
        ON discord_pending_messages(processed_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pending_message 
        ON discord_pending_messages(discord_message_id)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Tabela discord_pending_messages criada/atualizada")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)
EOF

echo -e "${GREEN}✅ Banco de dados configurado${NC}"

# 6. Configurar PM2
echo ""
echo "⚙️ Configurando PM2..."

# Iniciar com PM2
pm2 start "$SCRIPT_DIR/pm2.config.json"

# Salvar configuração
pm2 save

# Configurar startup automático
pm2 startup systemd -u $(whoami) --hp $HOME 2>/dev/null || true

echo -e "${GREEN}✅ PM2 configurado${NC}"

# 7. Status
echo ""
echo "📊 Status:"
pm2 status ralph-discord-bridge

echo ""
echo "===================================="
echo -e "${GREEN}✅ Setup completo!${NC}"
echo ""
echo "📋 Comandos úteis:"
echo "  pm2 logs ralph-discord-bridge    - Ver logs"
echo "  pm2 restart ralph-discord-bridge - Reiniciar"
echo "  pm2 stop ralph-discord-bridge    - Parar"
echo "  pm2 monit                         - Monitor"
echo ""
echo "🤖 Comandos no Discord:"
echo "  !ralph queue     - Ver fila de mensagens"
echo "  !ralph retry     - Reprocessar pendentes"
echo "  !ralph status    - Status do swarm"
echo ""
