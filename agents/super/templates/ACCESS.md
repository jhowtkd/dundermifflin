# Project Access Control

## Project: [NOME_DO_PROJETO]

### Permissions

**Full Access:**
- O Executivo (read, write, delete, admin)

**Write Access:**
- O Marketeiro (marketing/, research/, output/O-Marketeiro/)
- O Dev (technical/, infrastructure/, output/O-Dev/)

**Read Only:**
- All agents (context/, objectives/, decisions/)

### Restrictions
- O Marketeiro não modifica código sem aprovação do O Dev
- O Dev não modifica estratégia de marketing sem alinhamento
- Nenhum agente deleta entradas de DECISIONS.md (append only)
- Orçamento só pode ser alterado por O Executivo

### Communication Protocol
- Daily updates: Async no CONTEXT.md
- Blockers: Notificar imediatamente no chat
- Decisões críticas: Reunião de 15 min com O Executivo

### Last Updated
2026-02-09 by O Executivo
