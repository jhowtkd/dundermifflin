#!/bin/bash
# Instalador do Ralph Loop System

echo "🔄 Instalando Ralph Loop System..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Adicionar alias ao .bashrc se ainda não existe
if ! grep -q "ralph-loop" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Ralph Loop System" >> ~/.bashrc
    echo "alias ralph='$SCRIPT_DIR/ralph-loop.sh'" >> ~/.bashrc
    echo "alias ralph-dev='ralph dev --task'" >> ~/.bashrc
    echo "alias ralph-mkt='ralph marketeiro --task'" >> ~/.bashrc
    echo "alias ralph-exec='ralph executivo --task'" >> ~/.bashrc
    echo "✅ Aliases adicionados ao ~/.bashrc"
else
    echo "ℹ️ Aliases já existem no ~/.bashrc"
fi

# Criar diretórios necessários
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/results"

echo ""
echo "✅ Ralph Loop System instalado!"
echo ""
echo "Uso:"
echo "  ralph dev --task 'Criar API JWT'"
echo "  ralph marketeiro --task 'Escrever copy'"
echo "  ralph executivo --task 'Analisar métricas'"
echo ""
echo "Recarregue o shell ou execute: source ~/.bashrc"
