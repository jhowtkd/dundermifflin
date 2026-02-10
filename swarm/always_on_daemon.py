#!/usr/bin/env python3
"""
Ralph Swarm Always On - Script Standalone
Roda o sistema 24/7 em background

Uso:
  python3 always_on_daemon.py start  # Inicia
  python3 always_on_daemon.py stop   # Para
  python3 always_on_daemon.py status # Status
"""

import sys
import os
import time
import signal
import subprocess
from pathlib import Path

# PID file
PID_FILE = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/swarm/always_on.pid"
LOG_FILE = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/swarm/always_on.log"

def write_pid(pid):
    """Escreve PID em arquivo"""
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))

def read_pid():
    """Lê PID do arquivo"""
    if PID_FILE.exists():
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    return None

def remove_pid():
    """Remove arquivo PID"""
    if PID_FILE.exists():
        PID_FILE.unlink()

def is_running(pid):
    """Verifica se processo está rodando"""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

def start_daemon():
    """Inicia o daemon"""
    # Verificar se já está rodando
    pid = read_pid()
    if pid and is_running(pid):
        print(f"⚠️  Always On já está rodando (PID: {pid})")
        return
    
    print("🚀 Iniciando Ralph Swarm Always On...")
    
    # Fork para background
    try:
        pid = os.fork()
        if pid > 0:
            # Processo pai
            write_pid(pid)
            print(f"✅ Always On iniciado (PID: {pid})")
            print(f"📝 Log: {LOG_FILE}")
            return
    except AttributeError:
        # Windows não suporta fork
        pass
    
    # Processo filho (daemon)
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from always_on import AlwaysOnManager
        
        # Redirecionar output
        with open(LOG_FILE, 'a') as log:
            sys.stdout = log
            sys.stderr = log
            
            print(f"\n{'='*60}")
            print(f"Ralph Swarm Always On - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
            manager = AlwaysOnManager()
            manager.start()
            
            # Manter rodando
            while True:
                time.sleep(1)
                
    except Exception as e:
        with open(LOG_FILE, 'a') as log:
            log.write(f"\n❌ Erro: {e}\n")
        raise

def stop_daemon():
    """Para o daemon"""
    pid = read_pid()
    
    if not pid:
        print("⚠️  Always On não está rodando (sem PID)")
        return
    
    if not is_running(pid):
        print("⚠️  Always On não está rodando (processo morto)")
        remove_pid()
        return
    
    print(f"🛑 Parando Always On (PID: {pid})...")
    
    try:
        os.kill(pid, signal.SIGTERM)
        
        # Aguardar parada
        for _ in range(10):
            if not is_running(pid):
                break
            time.sleep(0.5)
        
        if is_running(pid):
            os.kill(pid, signal.SIGKILL)
        
        remove_pid()
        print("✅ Always On parado")
        
    except Exception as e:
        print(f"❌ Erro ao parar: {e}")

def status_daemon():
    """Mostra status"""
    pid = read_pid()
    
    if not pid:
        print("⭕ Always On: PARADO")
        return
    
    if is_running(pid):
        print(f"🟢 Always On: RODANDO (PID: {pid})")
        
        # Mostrar últimas linhas do log
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"\n📝 Últimas atividades:")
                    for line in lines[-5:]:
                        if line.strip():
                            print(f"   {line.strip()}")
    else:
        print(f"🔴 Always On: MORTO (PID: {pid} não existe)")
        remove_pid()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nComandos: start, stop, status")
        return
    
    command = sys.argv[1]
    
    if command == 'start':
        start_daemon()
    elif command == 'stop':
        stop_daemon()
    elif command == 'status':
        status_daemon()
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("Comandos: start, stop, status")

if __name__ == '__main__':
    main()
