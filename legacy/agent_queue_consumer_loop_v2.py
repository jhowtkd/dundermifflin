#!/usr/bin/env python3
"""
Agent Queue Consumer V2 - Loop Contínuo
Gerencia a fila - execução real é feita pelo OpenClaw via cron
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent_queue_consumer_v2 import main as consumer_main, logger

def main():
    logger.info("🚀 Agent Queue Consumer V2 (Fila + OpenClaw) iniciado")
    logger.info("⏱️ Intervalo: 30 segundos")
    logger.info("📋 Consumer gerencia fila | OpenClaw (cron) executa agentes")
    
    while True:
        try:
            consumer_main()
        except Exception as e:
            logger.error(f"❌ Erro no loop: {e}")
        
        time.sleep(30)

if __name__ == "__main__":
    main()
