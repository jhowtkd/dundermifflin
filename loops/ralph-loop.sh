#!/bin/bash
#
# Ralph Wiggum Loop System para Dunder Mifflin Super Agents
# Integração com Worker V3 + Tracking de Custos
#
# Uso: ./ralph-loop.sh <agente> [--max-iterations N] [--task "descrição"]
#
# Agentes disponíveis: dev, marketeiro, executivo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
LOGS_DIR="$SCRIPT_DIR/logs"
RESULTS_DIR="$SCRIPT_DIR/results"

# Criar diretórios necessários
mkdir -p "$LOGS_DIR" "$RESULTS_DIR"

# Configurações padrão
AGENT=""
MAX_ITERATIONS=20
COMPLETION_PROMISE="RALPH_COMPLETE"
TASK=""
DRY_RUN=false
LOOP_CODE=""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
    echo -e "${CYAN}Ralph Wiggum Loop - Sistema de Iteração para Super Agents${NC}"
    echo ""
    echo "Uso: $0 <agente> [opções]"
    echo ""
    echo -e "${BLUE}Agentes:${NC}"
    echo "  dev          - O Dev (desenvolvimento, código, arquitetura)"
    echo "  marketeiro   - O Marketeiro (copy, estratégia, criativos)"
    echo "  executivo    - O Executivo (gestão, análise, decisões)"
    echo ""
    echo -e "${BLUE}Opções:${NC}"
    echo "  --task, -t           Descrição específica da tarefa"
    echo "  --max-iterations, -m Número máximo de iterações (padrão: 20)"
    echo "  --completion, -c     String de completion (padrão: RALPH_COMPLETE)"
    echo "  --loop-code          Código de loop existente (para continuar)"
    echo "  --dry-run            Mostrar o prompt sem executar"
    echo "  --cost               Mostrar estimativa de custo"
    echo "  --help, -h           Mostrar esta ajuda"
    echo ""
    echo -e "${BLUE}Exemplos:${NC}"
    echo "  $0 dev --task 'Criar API de autenticação JWT'"
    echo "  $0 marketeiro --task 'Escrever copy para campanha' -m 30"
    echo "  $0 executivo --task 'Analisar métricas' --dry-run"
    echo ""
    echo -e "${CYAN}Dashboard:${NC} http://clawd-b450mhp:8888/ralph-dashboard.html"
}

log() {
    echo -e "${BLUE}[RALPH]${NC} $1"
}

success() {
    echo -e "${GREEN}[RALPH]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[RALPH]${NC} $1"
}

error() {
    echo -e "${RED}[RALPH]${NC} $1"
}

# Parse arguments
AGENT="${1:-}"

# Verificar se é help antes de fazer shift
if [[ "$AGENT" == "--help" ]] || [[ "$AGENT" == "-h" ]]; then
    usage
    exit 0
fi

shift || true

while [[ $# -gt 0 ]]; do
    case $1 in
        --task|-t)
            TASK="$2"
            shift 2
            ;;
        --max-iterations|-m)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --completion|-c)
            COMPLETION_PROMISE="$2"
            shift 2
            ;;
        --loop-code)
            LOOP_CODE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --cost)
            show_cost_estimate
            exit 0
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            error "Opção desconhecida: $1"
            usage
            exit 1
            ;;
    esac
done

# Validar agente
if [[ -z "$AGENT" ]]; then
    error "Agente não especificado"
    usage
    exit 1
fi

# Mapear nome do agente para slug
case "$AGENT" in
    dev|o-dev)
        AGENT_SLUG="o-dev"
        AGENT_NAME="O Dev"
        ;;
    marketeiro|o-marketeiro)
        AGENT_SLUG="o-marketeiro"
        AGENT_NAME="O Marketeiro"
        ;;
    executivo|o-executivo)
        AGENT_SLUG="o-executivo"
        AGENT_NAME="O Executivo"
        ;;
    *)
        error "Agente '$AGENT' não reconhecido. Use: dev, marketeiro, ou executivo"
        exit 1
        ;;
esac

PROMPT_FILE="$PROMPTS_DIR/${AGENT}-prompt.md"
if [[ ! -f "$PROMPT_FILE" ]]; then
    error "Prompt do agente não encontrado: $PROMPT_FILE"
    exit 1
fi

# Se não especificou task, mostrar erro
if [[ -z "$TASK" ]]; then
    error "Tarefa não especificada. Use --task 'descrição da tarefa'"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOGS_DIR/${AGENT}_${TIMESTAMP}.log"

# Função para criar loop no banco via Python
create_loop_in_db() {
    python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
from ralph_loop import create_loop
code = create_loop('$AGENT_SLUG', '''$TASK''', $MAX_ITERATIONS, '$COMPLETION_PROMISE')
print(code)
" 2>> "$LOGS_DIR/create_loop_errors.log"
}

# Função para logar iteração no banco
log_iteration_db() {
    local loop_code="$1"
    local iteration="$2"
    local prompt_summary="$3"
    local response_summary="$4"
    local tokens_in="${5:-0}"
    local tokens_out="${6:-0}"
    
    python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
from ralph_loop import log_iteration
log_iteration('$loop_code', $iteration, '''$prompt_summary''', '''$response_summary''', $tokens_in, $tokens_out)
" 2>> "$LOGS_DIR/${loop_code}_db_errors.log"
}

# Função para completar loop no banco
complete_loop_db() {
    local loop_code="$1"
    local result_path="$2"
    local success="$3"
    
    python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
from ralph_loop import complete_loop
with open('$result_path', 'r') as f:
    content = f.read()
complete_loop('$loop_code', content, True if '$success' == 'true' else False)
" 2>> "$LOGS_DIR/${loop_code}_db_errors.log"
}

show_cost_estimate() {
    log "Estimativa de custo (Kimi K2):"
    echo ""
    echo "Iterações | Tokens Est. | Custo Aprox."
    echo "----------|-------------|-------------"
    
    local iterations=(5 10 20 30 50)
    for i in "${iterations[@]}"; do
        # Estimativa: ~2K tokens in, ~1K tokens out por iteração
        local tokens_in=$((i * 2000))
        local tokens_out=$((i * 1000))
        # Preços Kimi K2: $0.001/1K in, $0.003/1K out
        local cost=$(echo "scale=4; ($tokens_in / 1000 * 0.001) + ($tokens_out / 1000 * 0.003)" | bc)
        printf "%9s | %8s in + %6s out | $%s\n" "$i" "$tokens_in" "$tokens_out" "$cost"
    done
    echo ""
    warn "Nota: Valores são estimativas. Custo real depende do tamanho dos prompts."
}

generate_prompt() {
    cat <<EOF
# MISSÃO: $TASK

## Contexto do Agente
$(cat "$PROMPT_FILE")

## Tarefa Específica
$TASK

## Instruções de Iteração
1. Analise o que já foi feito (se houver histórico abaixo)
2. Execute o próximo passo lógico da tarefa
3. Documente o que foi feito nesta iteração
4. Avalie se a tarefa está completa
5. Se completa, output: <$COMPLETION_PROMISE>
6. Se incompleta, liste os próximos passos

## Progresso Anterior
ITERATION_HISTORY

## Regras Importantes
- Não reinvente o que já foi feito
- Se encontrar erro, corrija e continue
- Se travar por mais de 3 iterações, documente o bloqueio
- Sempre mantenha o foco na tarefa original
- Output <$COMPLETION_PROMISE> apenas quando REALMENTE completo

## Métricas desta Iteração
Ao final, inclua:
- TOKENS_IN: [estimativa]
- TOKENS_OUT: [estimativa]

Execute agora:
EOF
}

# Dry run
if [[ "$DRY_RUN" == true ]]; then
    log "=== PROMPT QUE SERIA ENVIADO ==="
    generate_prompt | sed "s/ITERATION_HISTORY/[Nenhuma iteração anterior - primeira execução]/"
    log "================================"
    log "Agente: $AGENT_NAME ($AGENT_SLUG)"
    log "Max iterations: $MAX_ITERATIONS"
    log "Completion promise: $COMPLETION_PROMISE"
    
    # Mostrar estimativa de custo
    echo ""
    show_cost_estimate
    exit 0
fi

# Verificar se kimi CLI está disponível
KIMI_CMD=""
if command -v kimi &> /dev/null; then
    KIMI_CMD="kimi"
elif [[ -f "$HOME/.local/bin/kimi" ]]; then
    KIMI_CMD="$HOME/.local/bin/kimi"
elif [[ -f "/usr/local/bin/kimi" ]]; then
    KIMI_CMD="/usr/local/bin/kimi"
fi

if [[ -z "$KIMI_CMD" ]]; then
    error "kimi CLI não encontrado. Instale com: pip install kimi"
    exit 1
fi

# Criar ou recuperar loop no banco
if [[ -z "$LOOP_CODE" ]]; then
    LOOP_CODE=$(create_loop_in_db)
    if [[ -z "$LOOP_CODE" ]]; then
        error "Falha ao criar loop no banco de dados"
        exit 1
    fi
    log "Loop registrado: $LOOP_CODE"
else
    log "Continuando loop existente: $LOOP_CODE"
fi

# Iniciar loop
log "Iniciando Ralph Loop para: $AGENT_NAME"
log "Tarefa: $TASK"
log "Max iterations: $MAX_ITERATIONS"
log "Log: $LOG_FILE"
echo ""

ITERATION=0
HISTORY="[Nenhuma iteração anterior - primeira execução]"
COMPLETED=false
TOTAL_TOKENS_IN=0
TOTAL_TOKENS_OUT=0

while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
    ITERATION=$((ITERATION + 1))
    
    warn "=== ITERAÇÃO $ITERATION/$MAX_ITERATIONS ==="
    
    # Gerar prompt para esta iteração
    # Usar awk ao invés de sed para evitar problemas com caracteres especiais
    PROMPT=$(generate_prompt | awk -v hist="$HISTORY" '{gsub(/ITERATION_HISTORY/, hist); print}')
    
    # Salvar prompt desta iteração
    echo -e "\n\n=== ITERAÇÃO $ITERATION ===\n" >> "$LOG_FILE"
    echo "$PROMPT" >> "$LOG_FILE"
    echo -e "\n--- RESPOSTA ---\n" >> "$LOG_FILE"
    
    # Executar o agente
    TEMP_PROMPT=$(mktemp)
    TEMP_RESPONSE=$(mktemp)
    
    # Salvar prompt em arquivo (kimi não lê bem do pipe)
    echo "$PROMPT" > "$TEMP_PROMPT"
    
    log "Chamando $AGENT_NAME..."
    
    # Medir tempo
    START_TIME=$(date +%s)
    
    # Executar kimi lendo do arquivo
    if "$KIMI_CMD" -p "$TEMP_PROMPT" > "$TEMP_RESPONSE" 2>&1; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        RESPONSE=$(cat "$TEMP_RESPONSE")
        
        # Estimar tokens (aproximação: 1 token ~ 4 chars)
        TOKENS_IN=$((${#PROMPT} / 4))
        TOKENS_OUT=$((${#RESPONSE} / 4))
        TOTAL_TOKENS_IN=$((TOTAL_TOKENS_IN + TOKENS_IN))
        TOTAL_TOKENS_OUT=$((TOTAL_TOKENS_OUT + TOKENS_OUT))
        
        # Salvar resposta no log
        echo "$RESPONSE" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        echo "Duração: ${DURATION}s | Tokens: ${TOKENS_IN} in / ${TOKENS_OUT} out" >> "$LOG_FILE"
        
        # Logar no banco
        log_iteration_db "$LOOP_CODE" "$ITERATION" \
            "${PROMPT:0:200}..." \
            "${RESPONSE:0:500}..." \
            "$TOKENS_IN" "$TOKENS_OUT"
        
        # Verificar se completou
        if echo "$RESPONSE" | grep -q "$COMPLETION_PROMISE"; then
            success "✅ TAREFA COMPLETADA na iteração $ITERATION!"
            COMPLETED=true
            
            # Salvar resultado final
            RESULT_FILENAME="${LOOP_CODE}_${TIMESTAMP}.md"
            RESULT_PATH="$RESULTS_DIR/$RESULT_FILENAME"
            
            cat > "$RESULT_PATH" <<EOF
# Resultado Ralph Loop - $LOOP_CODE

**Agente:** $AGENT_NAME  
**Tarefa:** $TASK  
**Iterações:** $ITERATION/$MAX_ITERATIONS  
**Duração:** ${DURATION}s  
**Timestamp:** $(date)

## Resumo de Custos
- Total tokens in: $TOTAL_TOKENS_IN
- Total tokens out: $TOTAL_TOKENS_OUT
- Iterações: $ITERATION

## Resposta Final

$RESPONSE
EOF
            
            # Completar no banco
            complete_loop_db "$LOOP_CODE" "$RESULT_PATH" "true"
            
            success "Resultado salvo em: $RESULT_PATH"
            success "Dashboard: http://clawd-b450mhp:8888/ralph-dashboard.html"
            break
        fi
        
        # Atualizar histórico para próxima iteração
        HISTORY="Iteração $ITERATION (${DURATION}s, ${TOKENS_IN}/${TOKENS_OUT} tokens): $(echo "$RESPONSE" | head -3 | tr '\n' ' ' | cut -c1-150)..."
        
        log "Iteração $ITERATION completa em ${DURATION}s"
        warn "Total acumulado: ${TOTAL_TOKENS_IN} in / ${TOTAL_TOKENS_OUT} out tokens"
        echo ""
        
    else
        error "❌ Erro ao executar kimi CLI na iteração $ITERATION"
        echo "Erro: $(cat "$TEMP_RESPONSE")" >> "$LOG_FILE"
        rm "$TEMP_PROMPT" "$TEMP_RESPONSE"
        
        # Marcar como falha no banco
        RESULT_PATH="$RESULTS_DIR/${LOOP_CODE}_${TIMESTAMP}_FAILED.md"
        echo "# Loop Falhou - $LOOP_CODE" > "$RESULT_PATH"
        complete_loop_db "$LOOP_CODE" "$RESULT_PATH" "false"
        
        exit 1
    fi
    
    rm "$TEMP_PROMPT" "$TEMP_RESPONSE"
done

if [[ "$COMPLETED" == false ]]; then
    error "❌ MAX ITERATIONS ($MAX_ITERATIONS) atingido sem completion."
    warn "Tarefa pode estar bloqueada ou requer mais iterações."
    log "Log completo: $LOG_FILE"
    
    # Marcar como falha
    RESULT_PATH="$RESULTS_DIR/${LOOP_CODE}_${TIMESTAMP}_INCOMPLETE.md"
    echo "# Loop Incompleto - $LOOP_CODE" > "$RESULT_PATH"
    complete_loop_db "$LOOP_CODE" "$RESULT_PATH" "false"
    
    exit 1
fi

success "Ralph Loop finalizado com sucesso! 🎉"
success "Custo estimado: ~\$$(echo "scale=4; ($TOTAL_TOKENS_IN / 1000 * 0.001) + ($TOTAL_TOKENS_OUT / 1000 * 0.003)" | bc)"
exit 0
