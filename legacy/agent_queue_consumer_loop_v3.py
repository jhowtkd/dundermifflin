#!/usr/bin/env python3
"""
Agent Queue Consumer V3 - Loop Contínuo
Executa tarefas em loop - execução real com projetos
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent_queue_consumer_v3 import main as executor_main, logger

def main():
    logger.info("🚀 Agent Queue Consumer V3 (Executor) iniciado")
    logger.info("⏱️ Intervalo: 30 segundos")
    logger.info("🔧 Modo: EXECUÇÃO REAL com Git/GitHub + Projetos")
    
    while True:
        try:
            executor_main()
        except Exception as e:
            logger.error(f"❌ Erro no loop: {e}")
        
        time.sleep(30)

if __name__ == "__main__":
    main()
