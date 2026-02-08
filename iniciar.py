#!/usr/bin/env python3
"""
Iniciador Dunder Mifflin V2
Inicia servidor e abre navegador automaticamente
"""

import subprocess
import sys
import time
import os
import signal
import sqlite3
from pathlib import Path

def check_and_setup():
    """Verifica e configura o ambiente"""
    print("🔍 Verificando ambiente...")
    
    # Verifica banco
    db_path = Path("dunder_mifflin.db")
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        print("Execute: python3 import_jules.py")
        return False
    
    # Verifica tabelas
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services'")
    if not cur.fetchone():
        print("🔄 Executando migração...")
        import migrate_orchestration
        migrate_orchestration.migrate()
    conn.close()
    
    print("✅ Ambiente OK!")
    return True

def main():
    print("=" * 60)
    print("🏢 DUNDER MIFFLIN V2")
    print("=" * 60)
    
    if not check_and_setup():
        input("\nPressione Enter para sair...")
        return
    
    port = 3003
    url = f"http://localhost:{port}"
    
    print(f"\n🚀 Iniciando servidor na porta {port}...")
    print(f"🌐 URL: {url}")
    print("\n⏳ Aguardando servidor iniciar...")
    
    # Inicia servidor em subprocesso
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    process = subprocess.Popen(
        [sys.executable, "run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    
    # Aguarda servidor iniciar
    time.sleep(3)
    
    # Verifica se iniciou
    if process.poll() is not None:
        print("❌ Falha ao iniciar servidor!")
        output, _ = process.communicate()
        print(output)
        input("\nPressione Enter para sair...")
        return
    
    print("✅ Servidor rodando!")
    print(f"\n{'='*60}")
    print("📱 ABRA SEU NAVEGADOR E ACESSE:")
    print(f"   {url}")
    print(f"{'='*60}\n")
    
    # Abre navegador
    try:
        import webbrowser
        webbrowser.open(url)
        print("🌐 Navegador aberto automaticamente!")
    except:
        print("💡 Copie o URL acima e cole no navegador")
    
    print("\n⚠️  MANTENHA ESTA JANELA ABERTA!")
    print("Pressione Ctrl+C para parar o servidor\n")
    
    # Mostra logs do servidor
    try:
        while True:
            line = process.stdout.readline()
            if line:
                print(line, end='')
            if process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Parando servidor...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Servidor parado!")
    
    input("\nPressione Enter para fechar...")

if __name__ == "__main__":
    main()
