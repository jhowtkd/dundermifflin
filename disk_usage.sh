#!/bin/bash

#==============================================================================
# Nome: disk_usage.sh
# Descrição: Script para monitoramento de uso de disco dos diretórios principais
# Autor: Desenvolvedor Sênior
# Versão: 1.0.0
# Data: 2026-02-09
#==============================================================================

#------------------------------------------------------------------------------
# CONFIGURAÇÕES
#------------------------------------------------------------------------------

# Cores para saída formatada (definir como 'false' para desabilitar)
USAR_CORES=true

# Diretórios a serem monitorados (adicione ou remova conforme necessário)
DIRETORIOS=(
    "/"
    "/home"
    "/var"
    "/tmp"
    "/usr"
    "/opt"
    "/boot"
)

# Limite de alerta para uso de disco (porcentagem)
LIMITE_ALERTA=80
LIMITE_CRITICO=90

#------------------------------------------------------------------------------
# FUNÇÕES
#------------------------------------------------------------------------------

# Função para exibir mensagem de uso do script
mostrar_ajuda() {
    cat << EOF
Uso: $0 [OPÇÕES]

Script para monitoramento de uso de disco dos diretórios principais.

OPÇÕES:
    -h, --help      Mostra esta mensagem de ajuda
    -n, --no-color  Desabilita cores na saída
    -a, --all       Inclui todos os sistemas de arquivo montados
    -t, --top N     Mostra os N maiores diretórios (padrão: desabilitado)

EXEMPLOS:
    $0                    # Execução padrão
    $0 --no-color         # Execução sem cores
    $0 --all              # Mostra todos os sistemas de arquivo
    $0 --top 10           # Mostra os 10 maiores diretórios

EOF
}

# Função para configurar cores
configurar_cores() {
    if [[ "$USAR_CORES" == true ]]; then
        RESET='\033[0m'
        VERMELHO='\033[0;31m'
        VERDE='\033[0;32m'
        AMARELO='\033[0;33m'
        AZUL='\033[0;34m'
        MAGENTA='\033[0;35m'
        CIANO='\033[0;36m'
        BRANCO='\033[1;37m'
        BOLD='\033[1m'
    else
        RESET=''
        VERMELHO=''
        VERDE=''
        AMARELO=''
        AZUL=''
        MAGENTA=''
        CIANO=''
        BRANCO=''
        BOLD=''
    fi
}

# Função para imprimir linha separadora
linha_separadora() {
    printf "${CIANO}%s${RESET}\n" "───────────────────────────────────────────────────────────────────────────────"
}

# Função para imprimir cabeçalho
imprimir_cabecalho() {
    echo ""
    printf "${BOLD}${BRANCO}%s${RESET}\n" "                         USO DE DISCO - RELATÓRIO"
    printf "${AZUL}%s${RESET}\n" "                         Data: $(date '+%Y-%m-%d %H:%M:%S')"
    linha_separadora
}

# Função para imprimir cabeçalho da tabela
imprimir_cabecalho_tabela() {
    printf "${BOLD}%-20s %10s %10s %10s %8s %-20s${RESET}\n" \
        "Sistema de Arquivo" "Tamanho" "Usado" "Livre" "Uso%" "Montado em"
    linha_separadora
}

# Função para obter cor baseada na porcentagem de uso
obter_cor_porcentagem() {
    local porcentagem=$1
    
    if [[ $porcentagem -ge $LIMITE_CRITICO ]]; then
        echo "$VERMELHO"
    elif [[ $porcentagem -ge $LIMITE_ALERTA ]]; then
        echo "$AMARELO"
    else
        echo "$VERDE"
    fi
}

# Função para verificar se comando existe
comando_existe() {
    command -v "$1" &> /dev/null
}

# Função para mostrar uso de disco dos diretórios configurados
mostrar_uso_disco() {
    local mostrar_todos=$1
    
    imprimir_cabecalho
    echo -e "${BOLD}${MAGENTA}► Resumo Geral dos Sistemas de Arquivo${RESET}\n"
    
    imprimir_cabecalho_tabela
    
    if [[ "$mostrar_todos" == true ]]; then
        # Mostra todos os sistemas de arquivo montados
        df -h | awk 'NR>1 {
                printf "%-20s %10s %10s %10s %8s %-20s\n", $1, $2, $3, $4, $5, $6
            }' | while read -r linha; do
                # Extrai a porcentagem para colorir
                uso=$(echo "$linha" | awk '{gsub(/%/,""); print $5}')
                if [[ "$uso" =~ ^[0-9]+$ ]]; then
                    cor=$(obter_cor_porcentagem "$uso")
                    printf "${cor}%s${RESET}\n" "$linha"
                else
                    echo "$linha"
                fi
            done
    else
        # Mostra apenas os diretórios configurados
        for dir in "${DIRETORIOS[@]}"; do
            if [[ -d "$dir" ]]; then
                # Obtém informações do df para o diretório
                info=$(df -h "$dir" 2>/dev/null | awk 'NR==2 {
                    printf "%-20s %10s %10s %10s %8s %-20s", $1, $2, $3, $4, $5, $6
                }')
                
                if [[ -n "$info" ]]; then
                    # Extrai a porcentagem para colorir
                    uso=$(df "$dir" 2>/dev/null | awk 'NR==2 {gsub(/%/,""); print $5}')
                    cor=$(obter_cor_porcentagem "$uso")
                    printf "${cor}%s${RESET}\n" "$info"
                fi
            fi
        done
    fi
    
    linha_separadora
}

# Função para mostrar informações detalhadas por diretório
mostrar_detalhes_diretorio() {
    echo ""
    echo -e "${BOLD}${MAGENTA}► Detalhes por Diretório Principal${RESET}\n"
    
    for dir in "${DIRETORIOS[@]}"; do
        if [[ -d "$dir" ]]; then
            # Verifica se o diretório é acessível
            if [[ -r "$dir" ]]; then
                # Calcula o tamanho total do diretório
                tamanho=$(du -sh "$dir" 2>/dev/null | cut -f1)
                
                if [[ -n "$tamanho" ]]; then
                    printf "  ${AZUL}%-15s${RESET} ${VERDE}%10s${RESET}\n" "$dir" "$tamanho"
                fi
            else
                printf "  ${AZUL}%-15s${RESET} ${VERMELHO}%10s${RESET}\n" "$dir" "[Sem permissão]"
            fi
        else
            printf "  ${AZUL}%-15s${RESET} ${AMARELO}%10s${RESET}\n" "$dir" "[Não existe]"
        fi
    done
    
    linha_separadora
}

# Função para mostrar inodes
mostrar_inodes() {
    echo ""
    echo -e "${BOLD}${MAGENTA}► Uso de Inodes${RESET}\n"
    
    printf "${BOLD}%-20s %10s %10s %10s %8s %-20s${RESET}\n" \
        "Sistema de Arquivo" "Total" "Usado" "Livre" "Uso%" "Montado em"
    linha_separadora
    
    df -i | awk 'NR>1 {
        printf "%-20s %10s %10s %10s %8s %-20s\n", $1, $2, $3, $4, $5, $6
    }'
    
    linha_separadora
}

# Função para mostrar os maiores diretórios
mostrar_maiores_diretorios() {
    local quantidade=$1
    local diretorio_base="${2:-/}"
    
    echo ""
    echo -e "${BOLD}${MAGENTA}► Top ${quantidade} Maiores Subdiretórios em ${diretorio_base}${RESET}\n"
    
    if [[ -d "$diretorio_base" && -r "$diretorio_base" ]]; then
        printf "${BOLD}%-10s %-50s${RESET}\n" "Tamanho" "Diretório"
        linha_separadora
        
        du -h --max-depth=1 "$diretorio_base" 2>/dev/null | \
            sort -rh | \
            head -n "$quantidade" | \
            while read -r tamanho caminho; do
                printf "${VERDE}%-10s${RESET} ${AZUL}%s${RESET}\n" "$tamanho" "$caminho"
            done
        
        linha_separadora
    else
        echo -e "${VERMELHO}Erro: Diretório '${diretorio_base}' não existe ou sem permissão de leitura.${RESET}"
    fi
}

# Função para mostrar alertas de disco cheio
mostrar_alertas() {
    echo ""
    echo -e "${BOLD}${MAGENTA}► Alertas de Uso de Disco${RESET}\n"
    
    local alertas_encontrados=false
    
    while read -r filesystem size used avail percent mount; do
        # Pula o cabeçalho
        [[ "$filesystem" == "Filesystem" ]] && continue
        
        # Remove o % da porcentagem
        uso_num=$(echo "$percent" | tr -d '%')
        
        if [[ "$uso_num" -ge $LIMITE_CRITICO ]]; then
            printf "  ${VERMELHO}● CRÍTICO:${RESET} %-20s uso em %s\n" "$mount" "$percent"
            alertas_encontrados=true
        elif [[ "$uso_num" -ge $LIMITE_ALERTA ]]; then
            printf "  ${AMARELO}● ALERTA:${RESET}  %-20s uso em %s\n" "$mount" "$percent"
            alertas_encontrados=true
        fi
    done < <(df -h | tail -n +2)
    
    if [[ "$alertas_encontrados" == false ]]; then
        printf "  ${VERDE}✓ Todos os sistemas de arquivo estão abaixo do limite de ${LIMITE_ALERTA}%%${RESET}\n"
    fi
    
    linha_separadora
}

#------------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
#------------------------------------------------------------------------------

main() {
    local mostrar_todos=false
    local top_quantidade=0
    local diretorio_top="/"
    
    # Processa argumentos da linha de comando
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                mostrar_ajuda
                exit 0
                ;;
            -n|--no-color)
                USAR_CORES=false
                shift
                ;;
            -a|--all)
                mostrar_todos=true
                shift
                ;;
            -t|--top)
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    top_quantidade="$2"
                    shift 2
                else
                    echo -e "${VERMELHO}Erro: A opção --top requer um número.${RESET}"
                    exit 1
                fi
                ;;
            *)
                echo -e "${VERMELHO}Erro: Opção desconhecida: $1${RESET}"
                echo "Use '$0 --help' para ver as opções disponíveis."
                exit 1
                ;;
        esac
    done
    
    # Configura as cores
    configurar_cores
    
    # Verifica se o comando df está disponível
    if ! comando_existe df; then
        echo -e "${VERMELHO}Erro: O comando 'df' não está disponível neste sistema.${RESET}"
        exit 1
    fi
    
    # Mostra o relatório principal
    mostrar_uso_disco "$mostrar_todos"
    
    # Mostra detalhes adicionais
    mostrar_detalhes_diretorio
    
    # Mostra uso de inodes
    mostrar_inodes
    
    # Mostra alertas
    mostrar_alertas
    
    # Se solicitado, mostra os maiores diretórios
    if [[ $top_quantidade -gt 0 ]]; then
        mostrar_maiores_diretorios "$top_quantidade" "$diretorio_top"
    fi
    
    # Rodapé
    echo ""
    printf "${CIANO}%s${RESET}\n" "Relatório concluído."
    echo ""
}

#------------------------------------------------------------------------------
# EXECUÇÃO
#------------------------------------------------------------------------------

# Verifica se o script está sendo executado como root
if [[ $EUID -eq 0 ]]; then
    echo -e "${AMARELO}Aviso: Executando como root. Todos os diretórios serão acessíveis.${RESET}"
fi

# Executa a função principal com todos os argumentos
main "$@"
