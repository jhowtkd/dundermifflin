#!/bin/bash
#
# Health check e utilitários para Ralph Discord Bridge
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_DIR/dunder_mifflin.db"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo "Ralph Discord Bridge - Utilitários"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  status      - Mostra status completo do bot"
    echo "  health      - Verifica saúde do sistema"
    echo "  logs        - Mostra logs recentes"
    echo "  queue       - Mostra estatísticas da fila"
    echo "  retry       - Força reprocessamento da fila"
    echo "  restart     - Reinicia o bot"
    echo "  stop        - Para o bot"
    echo "  start       - Inicia o bot"
    echo "  monitor     - Abre monitor PM2"
    echo ""
}

cmd_status() {
    echo "🤖 Ralph Swarm - Status"
    echo "================================"
    echo ""
    
    # Status PM2
    echo "📊 Serviços PM2:"
    pm2 status 2>/dev/null || echo -e "${RED}  ❌ PM2 não está rodando${NC}"
    echo ""
    
    # Status do Monitor
    echo "🛡️  Task Monitor:"
    if pgrep -f "task_monitor.py" > /dev/null; then
        PID=$(pgrep -f "task_monitor.py" | head -1)
        echo -e "${GREEN}  ✅ Rodando (PID: $PID)${NC}"
    else
        echo -e "${RED}  ❌ Não encontrado${NC}"
    fi
    echo ""
    
    # Estatísticas da fila
    cmd_queue
    
    # Tasks recentes
    echo "📝 Tasks Recentes:"
    sqlite3 "$DB_PATH" "SELECT task_code, status, substr(original_request, 1, 40), datetime(created_at, 'localtime') FROM swarm_tasks ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "  Nenhuma task"
    echo ""
}

cmd_health() {
    echo "🏥 Health Check"
    echo "==============="
    echo ""
    
    local errors=0
    
    # 1. Verificar se PM2 está instalado
    echo -n "PM2 instalado: "
    if command -v pm2 > /dev/null; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        ((errors++))
    fi
    
    # 2. Verificar se bot está rodando
    echo -n "Bot rodando: "
    if pm2 pid ralph-discord-bridge > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        ((errors++))
    fi
    
    # 3. Verificar banco de dados
    echo -n "Banco acessível: "
    if sqlite3 "$DB_PATH" "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        ((errors++))
    fi
    
    # 4. Verificar tabela de fila
    echo -n "Tabela de fila: "
    if sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='discord_pending_messages';" | grep -q "discord_pending_messages"; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        ((errors++))
    fi
    
    # 5. Verificar token
    echo -n "Token Discord: "
    if grep -q "DISCORD_TOKEN=" "$SCRIPT_DIR/.env" 2>/dev/null; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        ((errors++))
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ Todos os checks passaram!${NC}"
    else
        echo -e "${RED}❌ $errors problema(s) encontrado(s)${NC}"
    fi
}

cmd_logs() {
    echo "📜 Logs Recentes:"
    echo "================="
    echo ""
    
    if [ -f "/tmp/discord_bridge.log" ]; then
        tail -50 /tmp/discord_bridge.log
    else
        pm2 logs ralph-discord-bridge --lines 50 --nostream
    fi
}

cmd_queue() {
    echo "📥 Fila de Mensagens:"
    
    if [ ! -f "$DB_PATH" ]; then
        echo -e "${RED}  ❌ Banco não encontrado${NC}"
        return
    fi
    
    local stats=$(sqlite3 "$DB_PATH" "SELECT 
        COUNT(CASE WHEN processed_at IS NULL THEN 1 END),
        COUNT(CASE WHEN processed_at IS NOT NULL THEN 1 END),
        COUNT(CASE WHEN retry_count >= 5 THEN 1 END)
    FROM discord_pending_messages;" 2>/dev/null)
    
    if [ -n "$stats" ]; then
        IFS='|' read -r pending processed failed <<< "$stats"
        echo "  Pendentes:  $pending"
        echo "  Processadas: $processed"
        echo "  Falhas:     $failed"
        
        if [ "$pending" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}💡 Use: !ralph retry no Discord${NC}"
        fi
    else
        echo "  Nenhuma mensagem na fila"
    fi
    echo ""
}

cmd_retry() {
    echo "🔄 Forçando reprocessamento..."
    
    # Atualiza mensagens pendentes para retry
    sqlite3 "$DB_PATH" "UPDATE discord_pending_messages 
        SET retry_count = 0, processed_at = NULL 
        WHERE processed_at IS NULL AND retry_count >= 5;" 2>/dev/null
    
    echo -e "${GREEN}✅ Mensagens atualizadas para retry${NC}"
    echo "   Aguarde 30 segundos para processamento automático"
}

cmd_restart() {
    echo "🔄 Reiniciando bot..."
    pm2 restart ralph-discord-bridge
    echo -e "${GREEN}✅ Reiniciado${NC}"
}

cmd_stop() {
    echo "🛑 Parando bot..."
    pm2 stop ralph-discord-bridge
    echo -e "${GREEN}✅ Parado${NC}"
}

cmd_start() {
    echo "▶️ Iniciando bot..."
    pm2 start "$SCRIPT_DIR/pm2.config.json"
    echo -e "${GREEN}✅ Iniciado${NC}"
}

cmd_monitor() {
    pm2 monit
}

# Main
case "${1:-status}" in
    status)
        cmd_status
        ;;
    health)
        cmd_health
        ;;
    logs)
        cmd_logs
        ;;
    queue)
        cmd_queue
        ;;
    retry)
        cmd_retry
        ;;
    restart)
        cmd_restart
        ;;
    stop)
        cmd_stop
        ;;
    start)
        cmd_start
        ;;
    monitor)
        cmd_monitor
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando desconhecido: $1${NC}"
        show_help
        exit 1
        ;;
esac
