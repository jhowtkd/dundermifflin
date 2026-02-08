#!/usr/bin/env python3
"""
Agent Queue Consumer - Loop Contínuo
Executa o consumer em loop a cada 30 segundos
"""

import time
import sys
from pathlib import Path

# Adiciona path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from agent_queue_consumer import process_tasks, logger

def main():
    logger.info("🚀 Agent Queue Consumer (Loop) iniciado")
    logger.info("⏱️ Intervalo: 30 segundos")
    
    while True:
        try:
            process_tasks()
        except Exception as e:
            logger.error(f"❌ Erro no loop: {e}")
        
        time.sleep(30)

if __name__ == "__main__":
    main()
