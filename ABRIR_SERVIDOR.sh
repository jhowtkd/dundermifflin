#!/bin/bash
# Script para abrir o servidor Dunder Mifflin

echo "🏢 Iniciando Dunder Mifflin V2..."
cd "$(dirname "$0")"

# Verifica se já está rodando
if lsof -Pi :3003 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Servidor já está rodando na porta 3003"
    echo "   Acesse: http://localhost:3003"
    open "http://localhost:3003"
    exit 0
fi

# Inicia servidor em background
echo "🚀 Iniciando servidor..."
python3 run_server.py &
SERVER_PID=$!

# Aguarda servidor subir
sleep 3

# Verifica se subiu
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Servidor rodando! (PID: $SERVER_PID)"
    echo "🌐 Abrindo navegador..."
    sleep 1
    open "http://localhost:3003"
    echo ""
    echo "💡 Para parar o servidor, execute:"
    echo "   kill $SERVER_PID"
else
    echo "❌ Falha ao iniciar servidor"
    exit 1
fi
