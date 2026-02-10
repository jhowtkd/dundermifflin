#!/usr/bin/env python3
"""
Teste de Stress do Ralph Loop - 10 Execuções
"""

import sys
sys.path.insert(0, '/home/clawd/.openclaw/workspace/projects/dunder-mifflin')

from ralph_loop import create_loop, get_db
import time

# 10 tarefas de teste variadas
tasks = [
    ("o-dev", "Criar função fibonacci(n: int) -> list que retorna sequência de Fibonacci até n termos"),
    ("o-marketeiro", "Escrever headline para produto de produtividade: 5 variações em tom profissional"),
    ("o-dev", "Criar classe Pessoa com atributos nome, idade e método apresentar()"),
    ("o-marketeiro", "Criar 3 bullets de benefícios para app de meditação"),
    ("o-dev", "Função validar_email(email: str) -> bool usando regex simples"),
    ("o-marketeiro", "Escrever CTA (call-to-action) para botão de download de ebook gratuito"),
    ("o-dev", "Criar função converter_celsius_fahrenheit(c: float) -> float"),
    ("o-marketeiro", "Headline para Black Friday: criar 3 opções com urgência"),
    ("o-dev", "Função calcular_media(notas: list[float]) -> float com tratamento de erro"),
    ("o-marketeiro", "Escrever descrição curta (150 chars) para app de fitness"),
]

print("🧪 TESTE DE STRESS - 10 LOOPS\n")
print("="*60)

results = {
    "completed": 0,
    "failed": 0,
    "total_time": 0,
    "total_tokens": 0
}

for i, (agent, task) in enumerate(tasks, 1):
    print(f"\n🔄 Teste {i}/10: {agent}")
    print(f"   Tarefa: {task[:50]}...")
    
    try:
        # Criar loop
        loop_code = create_loop(agent, task, max_iterations=5)
        print(f"   Código: {loop_code}")
        
        # Aguardar processamento (o cron job vai pegar)
        time.sleep(2)
        
        # Verificar status
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT status, current_iteration, total_tokens_in, total_tokens_out FROM ralph_loops WHERE loop_code = ?", (loop_code,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            status, iterations, tokens_in, tokens_out = row
            results["total_tokens"] += (tokens_in or 0) + (tokens_out or 0)
            
            if status == "completed":
                results["completed"] += 1
                print(f"   ✅ COMPLETED em {iterations} iterações")
            else:
                results["failed"] += 1
                print(f"   ❌ {status.upper()} em {iterations} iterações")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        results["failed"] += 1

print("\n" + "="*60)
print("📊 RESULTADOS DO TESTE:")
print(f"   ✅ Completados: {results['completed']}/10")
print(f"   ❌ Falhas: {results['failed']}/10")
print(f"   📊 Total tokens: {results['total_tokens']}")
print(f"   💰 Custo estimado: ${results['total_tokens'] * 0.000002:.4f}")
print("="*60)
