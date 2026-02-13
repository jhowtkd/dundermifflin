# Ralph Loops - Discord Integration

Sistema de iteração contínua para o Ralph do Discord.

## Fase 1: Estrutura Base ✅

### Arquivos Criados

- `loop_manager.py` - Gerenciador de loops com CRUD completo
- `schema.sql` - Schema SQL das tabelas
- `README.md` - Documentação
- `test_edge_cases.py` - Testes de edge cases

### Funcionalidades

- ✅ Criar loops com metadados do Discord
- ✅ Listar loops com filtros
- ✅ Logar iterações individuais
- ✅ Tracking de tokens/custo
- ✅ Status management (running, paused, completed, failed)
- ✅ Validação de agentes e status
- ✅ Foreign keys enforcement

### CLI

```bash
# Criar loop
python3 loop_manager.py create dev "Criar API" --max 25

# Listar loops
python3 loop_manager.py list --status running

# Testar
python3 loop_manager.py test
```

## Fase 2: Motor de Iteração ✅

### Arquivos Criados

- `iteration_engine.py` - Motor de execução de loops
- `llm_client.py` - Cliente para APIs de LLM
- `test_integration.py` - Testes de integração

### Funcionalidades

- ✅ Execução iterativa de loops
- ✅ Construção dinâmica de prompts
- ✅ Detecção de completion (RALPH_COMPLETE)
- ✅ Integração com LLM (modo mock/real)
- ✅ Callbacks de progresso (on_progress, on_complete, on_error)
- ✅ Estimativa de tokens e custo
- ✅ Relatórios completos de execução

## Fase 3: Integração Discord ✅

### Arquivos Criados

- `loop_commands.py` - Handler de comandos Discord
- Atualização: `discord_bridge.py` - Integração com bot existente

### Comandos Discord

```bash
# Iniciar loop
!ralph loop dev "Criar API de autenticação JWT" --max 20

# Listar loops
!ralph loops

# Status de um loop
!ralph loop status LOOP-ABC123

# Pausar/retomar
!ralph loop pause LOOP-ABC123
!ralph loop resume LOOP-ABC123

# Parar loop
!ralph loop stop LOOP-ABC123

# Histórico de iterações
!ralph loop history LOOP-ABC123

# Ajuda completa
!ralph loop help
```

### Funcionalidades

- ✅ Comandos Discord com embeds ricos
- ✅ Progresso em tempo real (edição de mensagens)
- ✅ Criação de loops com metadados Discord
- ✅ Listagem paginada de loops
- ✅ Status detalhado com custos
- ✅ Pausa/retoma/stop de loops
- ✅ Histórico de iterações

### Uso no Discord

```
[Usuário] !ralph loop dev "Criar API REST com Flask" --max 15

[Bot] 🚀 Iniciando Loop
      Agente: dev
      Max Iterações: 15
      Status: ▶️ Rodando
      Progresso: Iteração 0/15

[Bot] 📊 Iteração 1: running
      (atualizações em tempo real)

[Bot] ✅ Loop Completo: LOOP-ABC123
      Status: completed
      Iterações: 3/15
      Resumo: API criada com sucesso...
```

## Próximas Fases

- Fase 4: Polish & Dashboard Web
- Fase 5: Desativação Ralph Local
