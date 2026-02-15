#!/bin/bash
#
# Ralph Swarm - Startup Script
# Inicia Discord Bridge + Task Monitor + Worker Pool
#

set -e

PROJECT_DIR="/home/clawd/.openclaw/workspace/projects/dunder-mifflin"
SWARM_DIR="$PROJECT_DIR/swarm"
LOG_DIR="/tmp"

echo "🚀 Ralph Swarm - Startup"
echo "========================"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar dependências
log_info "Verificando dependências..."

if ! command -v python3 &> /dev/null; then
    log_error "python3 não encontrado"
    exit 1
fi

if ! command -v pm2 &> /dev/null; then
    log_warn "PM2 não encontrado. Instalando..."
    npm install -g pm2
fi

# 2. Verificar banco de dados
log_info "Verificando banco de dados..."
if [ ! -f "$PROJECT_DIR/dunder_mifflin.db" ]; then
    log_error "Banco de dados não encontrado: $PROJECT_DIR/dunder_mifflin.db"
    exit 1
fi

# 3. Parar instâncias antigas
log_info "Parando instâncias antigas..."
pm2 stop ralph-discord-bridge 2>/dev/null || true
pm2 delete ralph-discord-bridge 2>/dev/null || true
pkill -f "task_monitor.py" 2>/dev/null || true
pkill -f "worker_pool.py" 2>/dev/null || true

sleep 2

# 4. Backup do bridge
log_info "Fazendo backup..."
if [ -f "$SWARM_DIR/discord_bridge.py" ]; then
    cp "$SWARM_DIR/discord_bridge.py" "$SWARM_DIR/discord_bridge.py.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 5. Instalar nova versão do bridge
log_info "Instalando Discord Bridge v5.1..."
cp "$SWARM_DIR/discord_bridge_v51.py" "$SWARM_DIR/discord_bridge.py"

# 6. Iniciar Task Monitor em background
log_info "Iniciando Task Monitor..."
nohup python3 "$SWARM_DIR/task_monitor.py" > "$LOG_DIR/task_monitor.log" 2>&1 &
TASK_MONITOR_PID=$!
echo $TASK_MONITOR_PID > /tmp/task_monitor.pid
log_info "Task Monitor iniciado (PID: $TASK_MONITOR_PID)"

# 7. Iniciar Discord Bridge com PM2
log_info "Iniciando Discord Bridge..."
cd "$SWARM_DIR"
pm2 start pm2.config.json

# 8. Salvar configuração PM2
pm2 save

# 9. Status
log_info "Status dos serviços:"
echo ""
pm2 status
echo ""

# 10. Verificar se está rodando
if pgrep -f "task_monitor.py" > /dev/null; then
    log_info "✅ Task Monitor rodando"
else
    log_error "❌ Task Monitor não iniciou"
fi

if pm2 pid ralph-discord-bridge > /dev/null 2>&1; then
    log_info "✅ Discord Bridge rodando"
else
    log_error "❌ Discord Bridge não iniciou"
fi

echo ""
echo "========================"
echo -e "${GREEN}✅ Ralph Swarm iniciado!${NC}"
echo ""
echo "Comandos úteis:"
echo "  pm2 logs ralph-discord-bridge     # Ver logs do bot"
echo "  tail -f /tmp/task_monitor.log     # Ver logs do monitor"
echo "  ./ralphctl.sh status              # Status completo"
echo "  ./ralphctl.sh queue               # Ver fila de tasks"
echo ""
echo "Para parar:"
echo "  pm2 stop ralph-discord-bridge"
echo "  kill \$(cat /tmp/task_monitor.pid)"
