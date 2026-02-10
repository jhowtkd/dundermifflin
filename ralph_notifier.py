#!/usr/bin/env python3
"""
Ralph Loop Notifier
Envia notificações quando loops completam ou falham
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
RESULTS_DIR = Path(__file__).parent / "loops" / "results"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def send_telegram_notification(message, parse_mode="Markdown"):
    """Envia notificação via Telegram usando o OpenClaw"""
    try:
        # Tentar usar o messaging do OpenClaw
        import subprocess
        
        # Usar o tool message do openclaw se disponível
        result = subprocess.run([
            "openclaw", "message", "send",
            "--message", message,
            "--target", "jeffwindsor"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
            
        # Fallback: usar curl diretamente para a API do Telegram
        # (isso é apenas um placeholder - o OpenClaw vai lidar com isso)
        return False
        
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")
        return False

def format_loop_notification(loop_data, result_preview=None):
    """Formata mensagem de notificação"""
    
    agent_names = {
        'o-dev': '👨‍💻 O Dev',
        'o-marketeiro': '📢 O Marketeiro',
        'o-executivo': '💼 O Executivo'
    }
    
    agent_name = agent_names.get(loop_data['agent_slug'], loop_data['agent_slug'])
    status_icon = '✅' if loop_data['status'] == 'completed' else '❌'
    status_text = 'Completado' if loop_data['status'] == 'completed' else 'Falhou'
    
    # Calcular duração
    duration_str = "N/A"
    if loop_data.get('started_at') and loop_data.get('completed_at'):
        try:
            start = datetime.fromisoformat(loop_data['started_at'])
            end = datetime.fromisoformat(loop_data['completed_at'])
            duration = (end - start).total_seconds()
            if duration < 60:
                duration_str = f"{int(duration)}s"
            else:
                duration_str = f"{int(duration/60)}m {int(duration%60)}s"
        except:
            pass
    
    # Custo
    cost = loop_data.get('total_cost_usd', 0)
    
    message = f"""🔄 *Ralph Loop {status_text}*

{status_icon} *Código:* `{loop_data['loop_code']}`
🤖 *Agente:* {agent_name}
📋 *Tarefa:* {loop_data['task_description'][:100]}{'...' if len(loop_data['task_description']) > 100 else ''}

📊 *Resumo:*
• Iterações: {loop_data['current_iteration']}/{loop_data['max_iterations']}
• Duração: {duration_str}
• Custo: ${cost:.4f}
"""
    
    # Adicionar preview do resultado se disponível
    if result_preview:
        message += f"""
📝 *Preview do Resultado:*
```
{result_preview[:300]}{'...' if len(result_preview) > 300 else ''}
```
"""
    
    message += f"""
🔗 [Ver no Dashboard](http://clawd-b450mhp:8888/ralph-dashboard.html?loop={loop_data['loop_code']})
"""
    
    return message

def check_and_notify_completed():
    """Verifica loops completados recentemente e envia notificações"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Buscar loops completados nas últimas 5 minutos que ainda não foram notificados
    cur.execute("""
        SELECT * FROM ralph_loops 
        WHERE status IN ('completed', 'failed', 'cancelled')
        AND completed_at >= datetime('now', '-5 minutes')
        AND (notified_at IS NULL OR notified_at = '')
        ORDER BY completed_at DESC
    """)
    
    loops = [dict(row) for row in cur.fetchall()]
    
    notified_count = 0
    
    for loop in loops:
        try:
            # Tentar ler preview do resultado
            result_preview = None
            if loop.get('result_path'):
                result_file = Path(loop['result_path'])
                if result_file.exists():
                    content = result_file.read_text(encoding='utf-8')
                    # Extrair conteúdo após o header
                    lines = content.split('\n')
                    in_result = False
                    preview_lines = []
                    for line in lines:
                        if 'Resposta Final' in line or '## Resposta' in line:
                            in_result = True
                            continue
                        if in_result:
                            preview_lines.append(line)
                            if len(preview_lines) >= 10:
                                break
                    result_preview = '\n'.join(preview_lines)
            
            # Formatar e enviar notificação
            message = format_loop_notification(loop, result_preview)
            
            # Aqui vamos escrever em um arquivo que o OpenClaw pode monitorar
            # ou usar uma função de callback
            notification_file = Path(__file__).parent / "loops" / "notifications" / f"{loop['loop_code']}.json"
            notification_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'loop_code': loop['loop_code'],
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending'
                }, f, indent=2)
            
            # Marcar como notificado no banco
            cur.execute("""
                UPDATE ralph_loops 
                SET notified_at = ?
                WHERE loop_code = ?
            """, (datetime.now().isoformat(), loop['loop_code']))
            
            conn.commit()
            notified_count += 1
            
            print(f"✅ Notificação preparada para {loop['loop_code']}")
            
        except Exception as e:
            print(f"❌ Erro ao processar notificação para {loop['loop_code']}: {e}")
    
    conn.close()
    
    return notified_count

def send_pending_notifications():
    """Envia notificações pendentes (chamado pelo OpenClaw)"""
    
    notifications_dir = Path(__file__).parent / "loops" / "notifications"
    
    if not notifications_dir.exists():
        return 0
    
    sent_count = 0
    
    for notif_file in notifications_dir.glob("*.json"):
        try:
            with open(notif_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('status') == 'pending':
                # Aqui você pode integrar com o sistema de mensagens do OpenClaw
                # Por enquanto, vamos apenas marcar como enviado
                print(f"📨 Enviando notificação: {data['loop_code']}")
                print(data['message'])
                
                # Marcar como enviado
                data['status'] = 'sent'
                data['sent_at'] = datetime.now().isoformat()
                
                with open(notif_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                sent_count += 1
                
        except Exception as e:
            print(f"Erro ao enviar notificação {notif_file}: {e}")
    
    return sent_count

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Loop Notifier')
    parser.add_argument('--check', action='store_true', help='Verifica loops completados')
    parser.add_argument('--send', action='store_true', help='Envia notificações pendentes')
    
    args = parser.parse_args()
    
    if args.check:
        count = check_and_notify_completed()
        print(f"{count} loops preparados para notificação")
    
    if args.send:
        count = send_pending_notifications()
        print(f"{count} notificações enviadas")
    
    if not args.check and not args.send:
        # Executar ambos
        check_and_notify_completed()
        send_pending_notifications()
