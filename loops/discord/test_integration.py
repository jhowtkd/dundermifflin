#!/usr/bin/env python3
"""
Teste de integração completo - IterationEngine + LoopManager + LLMClient
"""

import os
import sys

# Ativar modo mock
os.environ['RALPH_MOCK_LLM'] = '1'

from loop_manager import LoopManager, LoopStatus
from iteration_engine import IterationEngine, EngineConfig

def test_full_flow():
    """Testa o fluxo completo de um loop"""
    print("🧪 Teste de Integração Completo")
    print("=" * 60)
    
    # Setup
    manager = LoopManager()
    config = EngineConfig(
        model='kimi-coding/k2p5',
        max_retries=1,
        completion_promise='RALPH_COMPLETE'
    )
    engine = IterationEngine(config=config, loop_manager=manager)
    
    # Pegar agente válido
    import sqlite3
    from pathlib import Path
    DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT slug FROM agents LIMIT 1")
    agent_row = cursor.fetchone()
    conn.close()
    
    if not agent_row:
        print("❌ Nenhum agente encontrado!")
        return False
    
    valid_agent = agent_row[0]
    print(f"\n📌 Agente: {valid_agent}")
    
    # Criar loop
    print("\n1. Criando loop...")
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description="Criar API de autenticação JWT",
        max_iterations=5,
        discord_channel_id="123456789",
        discord_user_id="987654321"
    )
    print(f"   ✅ Loop: {loop_code}")
    
    # Executar iterações
    print("\n2. Executando iterações...")
    
    progress_calls = []
    def on_progress(data):
        progress_calls.append(data)
        print(f"   📊 Iter {data['iteration']}: {data['status']}")
    
    completed_data = None
    def on_complete(data):
        nonlocal completed_data
        completed_data = data
        print(f"\n   ✅ Loop completado!")
        print(f"      Status: {data['status']}")
        print(f"      Iterações: {data['iterations']}")
    
    # Rodar loop
    engine.run_loop(
        loop_code=loop_code,
        model='kimi-coding/k2p5',
        on_progress=on_progress,
        on_complete=on_complete
    )
    
    # Verificar resultados
    print("\n3. Verificando resultados...")
    loop = manager.get_loop(loop_code)
    iterations = manager.get_iterations(loop_code)
    
    assert loop is not None, "Loop não encontrado"
    assert loop.status == LoopStatus.COMPLETED.value, f"Status não é completed: {loop.status}"
    assert loop.current_iteration > 0, "Nenhuma iteração executada"
    assert len(iterations) > 0, "Nenhuma iteração registrada"
    assert loop.total_tokens_in > 0, "Tokens não registrados"
    
    print(f"   ✅ Status: {loop.status}")
    print(f"   ✅ Iterações: {loop.current_iteration}")
    print(f"   ✅ Tokens: {loop.total_tokens_in} in / {loop.total_tokens_out} out")
    
    # Gerar relatório
    print("\n4. Gerando relatório...")
    report = engine.get_loop_report(loop_code)
    
    assert 'cost' in report
    assert 'tokens' in report
    assert 'iterations' in report
    
    print(f"   💰 Custo estimado: ${report['cost']['estimated_usd']}")
    print(f"   ⏱️  Tempo total: {report['timing']['total_seconds']}s")
    
    # Limpar
    print("\n5. Limpando...")
    manager.delete_loop(loop_code)
    print("   ✅ Loop deletado")
    
    print("\n" + "=" * 60)
    print("🎉 Todos os testes de integração passaram!")
    return True


def test_error_handling():
    """Testa tratamento de erros"""
    print("\n🧪 Teste de Tratamento de Erros")
    print("=" * 60)
    
    manager = LoopManager()
    engine = IterationEngine()
    
    # Testar loop inexistente (deve chamar on_error, não lançar exceção)
    print("\n1. Testando loop inexistente...")
    error_data = None
    
    def on_error(data):
        nonlocal error_data
        error_data = data
        print(f"   ⚠️  Erro capturado: {data['error']}")
    
    engine.run_loop('LOOP-INEXISTENTE-999', on_error=on_error)
    
    if error_data and 'Loop não encontrado' in error_data['error']:
        print("   ✅ Erro tratado corretamente via callback")
    else:
        print("   ❌ Erro não foi capturado corretamente")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Testes de erro passaram!")
    return True


if __name__ == "__main__":
    success = True
    
    try:
        if not test_full_flow():
            success = False
    except Exception as e:
        print(f"\n❌ Erro no teste de fluxo: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    try:
        if not test_error_handling():
            success = False
    except Exception as e:
        print(f"\n❌ Erro no teste de erros: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    if success:
        print("\n" + "=" * 60)
        print("🎉🎉🎉 TODOS OS TESTES PASSARAM! 🎉🎉🎉")
        print("=" * 60)
        print("\n✅ Fase 2 implementada com sucesso!")
        print("\nPróximos passos:")
        print("  - Fase 3: Integração Discord")
        print("  - Fase 4: Polish & Dashboard")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam")
        sys.exit(1)
