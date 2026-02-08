#!/usr/bin/env python3
"""
Script de inicialização local - Dunder Mifflin V2
Inicia API + disponibiliza frontend
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_dependencies():
    """Verifica se dependências estão instaladas"""
    try:
        import flask
        import flask_cors
        print("✅ Flask e Flask-CORS instalados")
        return True
    except ImportError:
        print("⚠️  Instalando dependências...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"], 
                      capture_output=True)
        return True

def check_database():
    """Verifica se banco existe e está populado"""
    db_path = Path("dunder_mifflin.db")
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        print("   Execute primeiro: python3 import_jules.py")
        return False
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Verifica se tabelas de orquestração existem
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services'")
    if not cur.fetchone():
        print("🔄 Executando migração de orquestração...")
        import migrate_orchestration
        migrate_orchestration.migrate()
    
    # Verifica se temos serviços
    cur.execute("SELECT COUNT(*) FROM services")
    count = cur.fetchone()[0]
    if count == 0:
        print("🌱 Populando serviços iniciais...")
        import migrate_orchestration
        migrate_orchestration.migrate()
    
    cur.execute("SELECT COUNT(*) FROM services WHERE is_active = 1")
    svc_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM agents WHERE is_active = 1")
    agent_count = cur.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Banco OK: {svc_count} serviços, {agent_count} agentes")
    return True

def main():
    print("=" * 60)
    print("🏢 DUNDER MIFFLIN V2 - Inicialização Local")
    print("=" * 60)
    
    # Verifica dependências
    check_dependencies()
    
    # Verifica banco
    if not check_database():
        sys.exit(1)
    
    port = os.getenv("DM_API_PORT", "3003")
    url = f"http://localhost:{port}"
    
    print(f"\n🌐 Iniciando servidor...")
    print(f"   URL: {url}")
    print(f"   API: {url}/api")
    print(f"\n📱 Páginas disponíveis:")
    print(f"   - Dashboard: {url}")
    print(f"   - Serviços:  {url}/services.html")
    print(f"   - Histórico: {url}/history.html")
    print("\n" + "=" * 60)
    print("Pressione Ctrl+C para parar")
    print("=" * 60 + "\n")
    
    # Abre navegador após 2 segundos
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Inicia Flask
    try:
        from api_flask import app
        app.run(host='0.0.0.0', port=int(port), debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
