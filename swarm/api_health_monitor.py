#!/usr/bin/env python3
"""
API Health Monitor - Watcher Integration
Monitora logs de erro da API e alerta quando thresholds são atingidos
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter

LOG_FILE = "/home/clawd/.openclaw/workspace/projects/dunder-mifflin/swarm/cost_log.jsonl"
ALERT_THRESHOLD_ERRORS = 3  # Alertar após 3 erros em 1 hora

class APIHealthMonitor:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def analyze_logs(self, hours=1):
        """Analisa logs das últimas N horas"""
        if not os.path.exists(LOG_FILE):
            return {"error": "Log file not found"}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        error_patterns = Counter()
        agent_errors = Counter()
        
        try:
            with open(LOG_FILE, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        
                        if entry_time >= cutoff_time and not entry['success']:
                            error_msg = entry.get('error', 'Unknown error')
                            error_patterns[error_msg] += 1
                            agent_errors[entry['agent']] += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as e:
            return {"error": str(e)}
        
        return {
            "period_hours": hours,
            "total_errors": sum(error_patterns.values()),
            "error_patterns": error_patterns,
            "agent_errors": agent_errors,
            "alert_needed": sum(error_patterns.values()) >= ALERT_THRESHOLD_ERRORS
        }
    
    def generate_report(self):
        """Gera relatório de saúde da API"""
        analysis = self.analyze_logs(hours=24)
        
        report = []
        report.append("=" * 50)
        report.append("👁️  WATCHER - API HEALTH REPORT")
        report.append(f"📅 Gerado em: {datetime.now().isoformat()}")
        report.append("=" * 50)
        
        if "error" in analysis:
            report.append(f"❌ Erro na análise: {analysis['error']}")
            return "\n".join(report)
        
        report.append(f"\n📊 Período: Últimas {analysis['period_hours']}h")
        report.append(f"🔴 Total de erros: {analysis['total_errors']}")
        
        if analysis['error_patterns']:
            report.append("\n📋 Padrões de Erro:")
            for error, count in analysis['error_patterns'].most_common():
                severity = "🔴" if count > 5 else "🟡" if count > 2 else "🟢"
                report.append(f"  {severity} {count}x: {error[:60]}...")
        
        if analysis['agent_errors']:
            report.append("\n🤖 Erros por Agente:")
            for agent, count in analysis['agent_errors'].most_common():
                report.append(f"  • {agent}: {count} erro(s)")
        
        if analysis['alert_needed']:
            report.append("\n🚨 ALERTA: Threshold de erros atingido!")
            report.append("   Ação recomendada: Verificar logs imediatamente")
        
        report.append("\n" + "=" * 50)
        return "\n".join(report)

if __name__ == "__main__":
    monitor = APIHealthMonitor()
    print(monitor.generate_report())
