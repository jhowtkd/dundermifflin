#!/usr/bin/env python3
"""
Start Script V2 - Inicia o sistema completo
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("🚀 Dunder Mifflin V2 - Iniciando Sistema")
    print("=" * 60)
    
    # Verifica se o banco existe
    db_path = Path("dunder_mifflin.db")
    if not db_path.exists():
        print("\n⚠️  Banco de dados não encontrado!")
        print("   Execute primeiro: python3 import_jules.py")
        sys.exit(1)
    
    # Verifica se os squads estão populados
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM squads")
    squad_count = cur.fetchone()[0]
    conn.close()
    
    if squad_count == 0:
        print("\n⚠️  Squads não encontrados!")
        print("   Execute: python3 seed_squads_v2.py")
        sys.exit(1)
    
    print(f"\n✅ Banco de dados OK ({squad_count} squads)")
    
    # Porta
    port = os.getenv("DM_API_PORT", "3003")
    
    print(f"\n🌐 Iniciando API na porta {port}...")
    print(f"   URL: http://localhost:{port}")
    print(f"   API: http://localhost:{port}/api/v2")
    print("\n" + "=" * 60)
    print("Pressione Ctrl+C para parar")
    print("=" * 60 + "\n")
    
    # Inicia a API
    try:
        subprocess.run([sys.executable, "api_v2.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Sistema parado")

if __name__ == "__main__":
    main()
