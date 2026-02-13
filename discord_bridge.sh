#!/bin/bash
# Ralph Swarm Discord Bridge Service
# Start/stop/status for Discord integration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="/tmp/ralph_discord_bridge.pid"
LOGFILE="$SCRIPT_DIR/logs/discord_bridge.log"

cd "$SCRIPT_DIR"

mkdir -p logs

start() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Discord bridge já está rodando (PID: $(cat $PIDFILE))"
        exit 1
    fi
    
    echo "🐝 Iniciando Ralph Discord Bridge..."
    nohup python3 swarm/discord_bridge.py >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "   PID: $(cat $PIDFILE)"
    echo "   Log: $LOGFILE"
    sleep 2
    
    if kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "   ✅ Bridge iniciado com sucesso!"
    else
        echo "   ❌ Falha ao iniciar. Verifique o log."
        rm -f "$PIDFILE"
    fi
}

stop() {
    if [ ! -f "$PIDFILE" ]; then
        echo "Discord bridge não está rodando"
        exit 1
    fi
    
    PID=$(cat "$PIDFILE")
    echo "🛑 Parando Discord Bridge (PID: $PID)..."
    kill "$PID" 2>/dev/null
    rm -f "$PIDFILE"
    echo "   ✅ Parado"
}

status() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "🐝 Discord Bridge: ✅ Rodando (PID: $(cat $PIDFILE))"
        echo "   Log tail:"
        tail -5 "$LOGFILE" 2>/dev/null || echo "   (sem log ainda)"
    else
        echo "🐝 Discord Bridge: ❌ Parado"
        rm -f "$PIDFILE" 2>/dev/null
    fi
}

restart() {
    stop
    sleep 1
    start
}

case "${1:-status}" in
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    status) status ;;
    *) echo "Uso: $0 {start|stop|restart|status}" ;;
esac
