#!/usr/bin/env python3
"""
Servidor Dunder Mifflin V2 - Script de execução standalone
"""

import os
import sys
import sqlite3
from pathlib import Path

# Adiciona diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

# Verifica banco
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
if not DB_PATH.exists():
    print("❌ Banco de dados não encontrado!")
    print("Execute: python3 import_jules.py")
    sys.exit(1)

# Verifica tabelas
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services'")
if not cur.fetchone():
    print("🔄 Executando migração...")
    import migrate_orchestration
    migrate_orchestration.migrate()
conn.close()

# Importa e roda Flask
from api_flask import app

port = int(os.getenv("DM_API_PORT", "3003"))

print(f"""
🏢 DUNDER MIFFLIN V2 - Servidor Iniciado
{'='*50}
🌐 URL: http://localhost:{port}
📊 API: http://localhost:{port}/api

📱 Páginas:
   • Dashboard: http://localhost:{port}
   • Serviços:  http://localhost:{port}/services.html
   • Histórico: http://localhost:{port}/history.html

⚠️  NÃO FECHE ESTA JANELA!
Pressione Ctrl+C para parar
{'='*50}
""")

app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
