#!/bin/bash
# Aliases simplificados para Ralph Loop
# Adicione ao ~/.bashrc: source ~/.openclaw/workspace/projects/dunder-mifflin/loops/aliases.sh

RALPH_DIR="$HOME/.openclaw/workspace/projects/dunder-mifflin/loops"

# Alias ultra-curto: ralph <agente> "tarefa"
ralph() {
    local agent="$1"
    shift
    local task="$*"
    
    if [[ -z "$agent" ]]; then
        echo "Uso: ralph <dev|marketeiro|executivo> 'tarefa'"
        echo "Ex: ralph dev 'Criar API de autenticação'"
        return 1
    fi
    
    if [[ -z "$task" ]]; then
        echo "❌ Erro: Tarefa não especificada"
        echo "Uso: ralph $agent 'descrição da tarefa'"
        return 1
    fi
    
    "$RALPH_DIR/ralph-loop.sh" "$agent" --task "$task"
}

# Comandos diretos por agente
ralph-dev() {
    "$RALPH_DIR/ralph-loop.sh" dev --task "$*"
}

ralph-mkt() {
    "$RALPH_DIR/ralph-loop.sh" marketeiro --task "$*"
}

ralph-exec() {
    "$RALPH_DIR/ralph-loop.sh" executivo --task "$*"
}

# Ver loops ativos
ralph-status() {
    echo "🔄 Loops ativos:"
    python3 -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/workspace/projects/dunder-mifflin')
from ralph_loop import get_active_loops
loops = get_active_loops()
if not loops:
    print('  Nenhum loop ativo')
else:
    for loop in loops:
        print(f\"  {loop['loop_code']} - {loop['agent_slug']} ({loop['current_iteration']}/{loop['max_iterations']})\")
        print(f\"    {loop['task_description'][:60]}...\")
"
}

# Últimos loops completados
ralph-history() {
    local limit="${1:-10}"
    echo "📜 Últimos $limit loops:"
    python3 -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/workspace/projects/dunder-mifflin')
from ralph_loop import get_loop_history
loops = get_loop_history(limit=$limit)
if not loops:
    print('  Nenhum loop no histórico')
else:
    for loop in loops:
        status = '✅' if loop['status'] == 'completed' else '❌'
        cost = loop.get('total_cost_usd', 0)
        print(f\"  {status} {loop['loop_code']} - {loop['agent_slug']}\")
        print(f\"     Iterações: {loop['current_iteration']} | Custo: \${cost:.4f}\")
        print(f\"     {loop['task_description'][:50]}...\")
"
}

# Custo total
ralph-cost() {
    echo "💰 Resumo de custos (últimos 7 dias):"
    python3 -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/workspace/projects/dunder-mifflin')
from ralph_loop import get_cost_summary
summary = get_cost_summary(days=7)
print(f\"  Total gasto: \${summary['total_cost_usd']:.4f}\")
print(f\"  Loops: {summary['completed']} completados, {summary['failed']} falhas\")
print(f\"  Taxa de sucesso: {summary['success_rate']*100:.1f}%\")
print(f\"  Total de iterações: {summary['total_iterations']}\")
"
}

# Preview do prompt (dry-run)
ralph-preview() {
    local agent="$1"
    shift
    local task="$*"
    
    if [[ -z "$agent" || -z "$task" ]]; then
        echo "Uso: ralph-preview <agente> 'tarefa'"
        return 1
    fi
    
    "$RALPH_DIR/ralph-loop.sh" "$agent" --task "$task" --dry-run
}

# Ajuda
ralph-help() {
    cat <<'EOF'
🔄 RALPH LOOP - Comandos Rápidos

Acesso:
  Local:    http://clawd-b450mhp:8888/ralph-start.html
  Tailscale: http://100.94.223.52:8888/ralph-start.html

Uso básico:
  ralph dev "Criar função de validar CPF"
  ralph marketeiro "Escrever copy para anúncio"
  ralph executivo "Analisar métricas do mês"

Comandos diretos:
  ralph-dev "tarefa"      # O Dev - desenvolvimento
  ralph-mkt "tarefa"      # O Marketeiro - marketing
  ralph-exec "tarefa"     # O Executivo - gestão

Monitoramento:
  ralph-status            # Ver loops ativos
  ralph-history [N]       # Últimos N loops (padrão: 10)
  ralph-cost              # Resumo de custos

Utilitários:
  ralph-preview dev "tarefa"  # Ver prompt sem executar

Exemplos:
  ralph dev "API REST com Flask"
  ralph-mkt "5 variações de headline"
  ralph-exec "Relatório de ROI Q4"
EOF
}

# Auto-complete (se bash-completion estiver instalado)
if type complete >/dev/null 2>&1; then
    complete -W "dev marketeiro executivo" ralph
    complete -W "dev marketeiro executivo" ralph-preview
fi

echo "✅ Aliases Ralph Loop carregados!"
echo "   Digite 'ralph-help' para ver os comandos"
