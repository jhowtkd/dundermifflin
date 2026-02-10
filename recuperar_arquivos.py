#!/usr/bin/env python3
"""
Recupera arquivos dos planos de execução que já foram completados
mas não geraram arquivos físicos.
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
STUDIO_DIR = Path.home() / ".openclaw/workspace/studio/projects/dunder_mifflin"

def extract_outputs_from_result(result_text):
    """Extrai outputs dos resultados do agente"""
    outputs = []
    
    # Padrão para encontrar blocos de resultado por agente
    agent_pattern = r'---\s*(\w+)\s*---\n+(.*?)(?=---|\Z)'
    matches = re.findall(agent_pattern, result_text, re.DOTALL)
    
    for agent_slug, content in matches:
        # Tenta extrair o output JSON
        try:
            # Procura por JSON no conteúdo
            json_match = re.search(r'\{[^}]*"output"[^}]*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                output_text = data.get('output', content)
            else:
                output_text = content[:2000]  # Pega primeiros 2000 chars
            
            outputs.append({
                'agent': agent_slug,
                'content': output_text
            })
        except:
            outputs.append({
                'agent': agent_slug,
                'content': content[:2000]
            })
    
    return outputs

def save_blog_post(title, content, date_str):
    """Salva post de blog"""
    blog_dir = STUDIO_DIR / "blog_posts"
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
    filename = f"{date_str}_blog_{safe_title}.md"
    filepath = blog_dir / filename
    
    md_content = f"""# {title}

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Tipo:** Post de Blog

---

{content}

---

*Gerado por Dunder Mifflin 🏢*
"""
    filepath.write_text(md_content, encoding="utf-8")
    print(f"   💾 Blog: {filepath.name}")
    return str(filepath)

def save_tiktok_scripts(title, content, date_str):
    """Salva roteiros TikTok"""
    tiktok_dir = STUDIO_DIR / "tiktok_scripts"
    tiktok_dir.mkdir(parents=True, exist_ok=True)
    
    safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
    filename = f"{date_str}_tiktok_{safe_title}.md"
    filepath = tiktok_dir / filename
    
    md_content = f"""# {title}

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Tipo:** Roteiros TikTok

---

{content}

---

*Gerado por Dunder Mifflin 🏢*
"""
    filepath.write_text(md_content, encoding="utf-8")
    print(f"   💾 TikTok: {filepath.name}")
    return str(filepath)

def save_repurposed_content(title, contents_dict, date_str):
    """Salva conteúdo repurposed"""
    repurpose_dir = STUDIO_DIR / "repurposed_content"
    repurpose_dir.mkdir(parents=True, exist_ok=True)
    
    safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
    filename = f"{date_str}_repurpose_{safe_title}.md"
    filepath = repurpose_dir / filename
    
    md_content = f"""# {title}

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Tipo:** Conteúdo Repurposed

---

"""
    for section, content in contents_dict.items():
        md_content += f"\n## {section}\n\n{content}\n\n---\n"
    
    md_content += "\n*Gerado por Dunder Mifflin 🏢*"
    
    filepath.write_text(md_content, encoding="utf-8")
    print(f"   💾 Repurposed: {filepath.name}")
    return str(filepath)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Busca planos completados sem arquivos (19-22)
    cur.execute("""
        SELECT id, title, final_result, created_at 
        FROM execution_plans 
        WHERE id IN (19, 20, 21, 22) AND final_result IS NOT NULL
    """)
    
    plans = cur.fetchall()
    print(f"🔍 Encontrados {len(plans)} planos para recuperar\n")
    
    for plan in plans:
        plan_id = plan['id']
        title = plan['title']
        result = plan['final_result']
        created = plan['created_at']
        
        # Extrai data do created_at
        date_str = created[:10].replace('-', '') if created else datetime.now().strftime('%Y%m%d')
        
        print(f"📋 Plano #{plan_id}: {title[:50]}...")
        
        # Extrai outputs dos resultados
        outputs = extract_outputs_from_result(result)
        
        for output in outputs:
            agent = output['agent'].lower()
            content = output['content']
            
            # Decide onde salvar baseado no agente
            if 'copywriter' in agent:
                save_blog_post(f"{title} - Blog", content, date_str)
            elif 'twitter' in agent:
                save_tiktok_scripts(f"{title} - Twitter", content, date_str)
            elif 'linkedin' in agent:
                save_blog_post(f"{title} - LinkedIn", content, date_str)
            elif 'instagram' in agent or 'visual' in agent:
                save_tiktok_scripts(f"{title} - Instagram", content, date_str)
            elif 'strategist' in agent or 'tiktok' in agent:
                save_tiktok_scripts(f"{title} - TikTok", content, date_str)
        
        # Se for plano de repurpose, salva tudo junto
        if 'repurpose' in title.lower() or 'formatos' in title.lower():
            contents_dict = {o['agent']: o['content'][:1000] for o in outputs}
            if contents_dict:
                save_repurposed_content(title, contents_dict, date_str)
        
        print()
    
    conn.close()
    print("✅ Recuperação concluída!")

if __name__ == "__main__":
    main()
