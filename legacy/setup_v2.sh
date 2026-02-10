#!/bin/bash
# Setup Dunder Mifflin V2

echo "🏢 Dunder Mifflin V2 - Setup"
echo "============================"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

echo "✅ Python encontrado"

# Verifica dependências
pip3 install flask flask-cors 2>/dev/null || pip install flask flask-cors 2>/dev/null

echo "✅ Dependências instaladas"

# Inicializa banco se não existir
if [ ! -f "dunder_mifflin.db" ]; then
    echo "🗄️  Criando banco de dados..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('dunder_mifflin.db')
with open('schema_v2.sql', 'r') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print('✅ Banco criado')
"
fi

# Importa agentes
if [ -d "agents" ]; then
    echo "🤖 Importando agentes Jules..."
    python3 import_jules.py
fi

# Popula squads
echo "👥 Criando squads..."
python3 seed_squads_v2.py

echo ""
echo "============================"
echo "✅ Setup completo!"
echo ""
echo "Para iniciar:"
echo "  python3 start_v2.py"
echo ""
echo "Acesse: http://localhost:3003"
echo "============================"
