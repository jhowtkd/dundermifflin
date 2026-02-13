#!/usr/bin/env python3
"""
Testes de Edge Cases para LoopManager (Atualizado)
"""

from loop_manager import LoopManager, LoopStatus

print('🔍 Testes de Edge Cases e Validação (Corrigido)')
print('=' * 60)

manager = LoopManager()

# Pegar um agente válido do banco
import sqlite3
from pathlib import Path
DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT slug FROM agents LIMIT 1")
valid_agent = cursor.fetchone()[0]
conn.close()

print(f'✅ Usando agente válido: {valid_agent}')

# Test 1: Campos nulos
print('\n1. Testando campos nulos...')
try:
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description='Teste nulos',
        discord_channel_id=None,
        discord_user_id=None,
        discord_guild_id=None,
        task_code=None
    )
    loop = manager.get_loop(loop_code)
    assert loop.discord_channel_id is None
    print('   ✅ Campos nulos aceitos corretamente')
except Exception as e:
    print(f'   ❌ Erro: {e}')

# Test 2: Caracteres especiais
print('\n2. Testando caracteres especiais...')
try:
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description="Teste com ' apóstrofo e \"aspas\" e -- hífen",
        discord_channel_id='123\"456'
    )
    loop = manager.get_loop(loop_code)
    assert "apóstrofo" in loop.task_description
    print('   ✅ Caracteres especiais tratados')
except Exception as e:
    print(f'   ❌ Erro: {e}')

# Test 3: Agente inexistente (deve falhar agora)
print('\n3. Testando agente inexistente (deve rejeitar)...')
try:
    loop_code = manager.create_loop(
        agent_slug='agente_inexistente_12345',
        task_description='Teste FK'
    )
    print('   ❌ Agente inexistente foi aceito (BUG!)')
except ValueError as e:
    print(f'   ✅ Agente inexistente rejeitado: {e}')
except Exception as e:
    print(f'   ⚠️  Erro inesperado: {e}')

# Test 4: Status inválido (deve falhar agora)
print('\n4. Testando status inválido (deve rejeitar)...')
try:
    # Primeiro criar um loop válido
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description='Teste status'
    )
    # Tentar atualizar com status inválido
    manager.update_loop_status(loop_code, 'status_invalido_123')
    print('   ❌ Status inválido foi aceito (BUG!)')
except ValueError as e:
    print(f'   ✅ Status inválido rejeitado: {e}')
except Exception as e:
    print(f'   ⚠️  Erro inesperado: {e}')

# Test 5: Status válidos
print('\n5. Testando status válidos...')
try:
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description='Teste status válidos'
    )
    for status in [LoopStatus.RUNNING, LoopStatus.PAUSED, LoopStatus.COMPLETED]:
        manager.update_loop_status(loop_code, status.value)
        loop = manager.get_loop(loop_code)
        assert loop.status == status.value
    print(f'   ✅ Todos os status válidos funcionam')
except Exception as e:
    print(f'   ❌ Erro: {e}')

# Test 6: Loop inexistente
print('\n6. Testando loop inexistente...')
loop = manager.get_loop('LOOP-INEXISTENTE-999')
if loop is None:
    print('   ✅ Retorna None para loop inexistente')
else:
    print('   ❌ Deveria retornar None')

# Test 7: Deletar loop inexistente
print('\n7. Testando delete de loop inexistente...')
result = manager.delete_loop('LOOP-INEXISTENTE-999')
if not result:
    print('   ✅ Delete retorna False para loop inexistente')
else:
    print('   ❌ Deveria retornar False')

# Test 8: Atualizar status de loop inexistente
print('\n8. Testando update de loop inexistente...')
try:
    result = manager.update_loop_status('LOOP-INEXISTENTE-999', LoopStatus.COMPLETED.value)
    if not result:
        print('   ✅ Update retorna False para loop inexistente')
    else:
        print('   ❌ Deveria retornar False')
except Exception as e:
    print(f'   ❌ Erro: {e}')

# Test 9: Listar iterações de loop inexistente
print('\n9. Testando get_iterations de loop inexistente...')
iterations = manager.get_iterations('LOOP-INEXISTENTE-999')
if len(iterations) == 0:
    print('   ✅ Retorna lista vazia para loop inexistente')
else:
    print('   ❌ Deveria retornar lista vazia')

# Test 10: Unicidade de códigos
print('\n10. Verificando unicidade de loop_code...')
codes = set()
for i in range(10):
    code = manager._generate_loop_code()
    assert code not in codes
    codes.add(code)
print(f'   ✅ 10 códigos gerados, todos únicos')

# Test 11: Task muito longa
print('\n11. Testando task description longa...')
try:
    long_task = "A" * 10000  # 10KB de texto
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description=long_task
    )
    loop = manager.get_loop(loop_code)
    assert len(loop.task_description) == 10000
    print('   ✅ Task longa aceita (10KB)')
except Exception as e:
    print(f'   ⚠️  Erro com task longa: {e}')

# Test 12: Iteração completa
print('\n12. Testando fluxo completo de iteração...')
try:
    loop_code = manager.create_loop(
        agent_slug=valid_agent,
        task_description='Teste fluxo completo',
        max_iterations=5
    )
    
    # Logar 3 iterações
    for i in range(1, 4):
        manager.log_iteration(
            loop_code=loop_code,
            iteration_number=i,
            prompt_summary=f'Iteração {i}: Análise',
            response_summary=f'Resultado {i}: Concluído',
            tokens_in=1500,
            tokens_out=800,
            duration_seconds=12
        )
        manager.increment_iteration(loop_code, 1500, 800)
    
    # Completar
    manager.update_loop_status(loop_code, LoopStatus.COMPLETED.value, 'Concluído com sucesso')
    
    # Verificar
    loop = manager.get_loop(loop_code)
    iterations = manager.get_iterations(loop_code)
    
    assert loop.status == 'completed'
    assert loop.current_iteration == 3
    assert len(iterations) == 3
    assert loop.total_tokens_in == 4500
    assert loop.total_tokens_out == 2400
    
    print('   ✅ Fluxo completo funcionou')
    print(f'      - Iterações: {loop.current_iteration}')
    print(f'      - Tokens: {loop.total_tokens_in} in / {loop.total_tokens_out} out')
    print(f'      - Status: {loop.status}')
except Exception as e:
    print(f'   ❌ Erro: {e}')

print('\n' + '=' * 60)
print('✅ Testes de edge cases completos (com correções)')
