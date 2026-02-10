#!/usr/bin/env python3
"""
Auditor Automático de Interface - Dunder Mifflin
Verifica consistência das telas, design system e integração API
"""

import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Configurações
FRONTEND_DIR = Path("/home/clawd/.openclaw/workspace/projects/dunder-mifflin/frontend")
API_BASE = "http://100.94.223.52:3003/api"
OUTPUT_DIR = Path("/home/clawd/.openclaw/workspace/projects/dunder-mifflin")

# Especificação esperada
EXPECTED_SCREENS = {
    "index.html": {"title": "Dashboard Principal", "required": True},
    "agents.html": {"title": "Fichas dos Agentes", "required": True},
    "missions.html": {"title": "Lista de Missões", "required": True},
    "mission-detail.html": {"title": "Detalhes da Missão", "required": True},
    "proposals.html": {"title": "Criar Propostas", "required": True},
    "files.html": {"title": "Arquivos Gerados", "required": True},
    "services.html": {"title": "Catálogo de Serviços", "required": True},
    "history.html": {"title": "Histórico", "required": True},
}

# Design System Win95
WIN95_VARS = {
    "--win-bg": "#c0c0c0",
    "--win-highlight": "#ffffff",
    "--win-shadow": "#808080",
    "--win-dark": "#404040",
    "--win-blue": "#000080",
    "--win-blue-light": "#1084d0",
}

EXPECTED_FONTS = ["Space Grotesk", "VT323"]

class InterfaceAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.ok_items = []
        self.api_status = {}
        
    def log_issue(self, severity: str, screen: str, description: str):
        """Registra um problema encontrado"""
        self.issues.append({
            "severity": severity,
            "screen": screen,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_ok(self, screen: str, description: str):
        """Registra item verificado com sucesso"""
        self.ok_items.append({
            "screen": screen,
            "description": description
        })
    
    def check_screen_exists(self, filename: str) -> bool:
        """Verifica se uma tela existe"""
        filepath = FRONTEND_DIR / filename
        exists = filepath.exists()
        
        if not exists and EXPECTED_SCREENS[filename]["required"]:
            self.log_issue("🔴 CRÍTICO", filename, f"Tela obrigatória não existe: {filename}")
        elif exists:
            self.log_ok(filename, f"Tela existe ({filepath.stat().st_size} bytes)")
            
        return exists
    
    def analyze_design_consistency(self, filename: str) -> Dict:
        """Analisa consistência do design Win95"""
        filepath = FRONTEND_DIR / filename
        if not filepath.exists():
            return {}
            
        content = filepath.read_text(encoding='utf-8')
        findings = {
            "uses_tailwind": False,
            "win95_vars_present": [],
            "win95_vars_missing": [],
            "expected_fonts_present": [],
            "has_win95_window": False,
            "has_crt_effect": False,
        }
        
        # Verifica Tailwind
        if "tailwindcss" in content or "tailwind" in content:
            findings["uses_tailwind"] = True
            self.log_issue("🟡 MÉDIO", filename, "Usa Tailwind CSS (inconsistente com design Win95)")
        
        # Verifica variáveis Win95
        for var, value in WIN95_VARS.items():
            if var in content:
                findings["win95_vars_present"].append(var)
            else:
                findings["win95_vars_missing"].append(var)
        
        if findings["win95_vars_missing"]:
            self.log_issue("🟢 BAIXO", filename, f"Variáveis Win95 faltando: {', '.join(findings['win95_vars_missing'][:3])}")
        
        # Verifica fontes
        for font in EXPECTED_FONTS:
            if font in content:
                findings["expected_fonts_present"].append(font)
        
        # Verifica estrutura Win95
        if ".window" in content and "win-bg" in content:
            findings["has_win95_window"] = True
        
        # Verifica efeito CRT
        if "crt-overlay" in content or "scanline" in content.lower():
            findings["has_crt_effect"] = True
            
        return findings
    
    def check_api_integration(self, filename: str) -> List[str]:
        """Verifica endpoints API utilizados"""
        filepath = FRONTEND_DIR / filename
        if not filepath.exists():
            return []
            
        content = filepath.read_text(encoding='utf-8')
        endpoints = []
        
        # Regex para encontrar chamadas API
        api_patterns = [
            r'fetch\([\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
            r'API_BASE\s*=\s*[\'"`]([^\'"`]*)[\'"`]',
            r'url:\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endpoints.extend(matches)
        
        if endpoints:
            self.log_ok(filename, f"Integração API: {len(endpoints)} endpoint(s) encontrado(s)")
        else:
            self.log_issue("🟡 MÉDIO", filename, "Nenhuma integração API encontrada")
            
        return list(set(endpoints))
    
    def check_navigation(self, filename: str) -> Dict:
        """Verifica navegação da tela"""
        filepath = FRONTEND_DIR / filename
        if not filepath.exists():
            return {}
            
        content = filepath.read_text(encoding='utf-8')
        
        # Encontra todos os links
        links = re.findall(r'href=["\']([^"\']+\.html)["\']', content)
        
        # Verifica se tem link para outras telas principais
        main_links = {
            "index": "index.html" in content,
            "agents": "agents.html" in content,
            "missions": "missions.html" in content,
            "services": "services.html" in content,
            "history": "history.html" in content,
        }
        
        nav_score = sum(main_links.values())
        
        if nav_score < 2 and filename != "index.html":
            self.log_issue("🟡 MÉDIO", filename, f"Navegação limitada (só {nav_score} links principais)")
        elif nav_score >= 2:
            self.log_ok(filename, f"Navegação OK ({nav_score} links principais)")
            
        return {
            "links_found": links,
            "main_links": main_links,
            "score": nav_score
        }
    
    def test_api_health(self):
        """Testa saúde da API"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                self.api_status["health"] = "✅ OK"
                self.log_ok("API", "Endpoint /health respondendo")
            else:
                self.api_status["health"] = f"⚠️ Status {response.status_code}"
                self.log_issue("🔴 CRÍTICO", "API", f"/health retornou {response.status_code}")
        except Exception as e:
            self.api_status["health"] = f"❌ Erro: {str(e)[:50]}"
            self.log_issue("🔴 CRÍTICO", "API", f"Não conseguiu conectar: {str(e)[:50]}")
    
    def generate_report(self) -> str:
        """Gera relatório Markdown"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report = f"""# Relatório de Auditoria - Interface Dunder Mifflin

**Data:** {now}  
**Auditor:** Script Automático  
**Versão:** v1.0

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| Telas existentes | {sum(1 for s in EXPECTED_SCREENS if (FRONTEND_DIR / s).exists())}/{len(EXPECTED_SCREENS)} |
| Críticos | {sum(1 for i in self.issues if i['severity'] == '🔴 CRÍTICO')} |
| Médios | {sum(1 for i in self.issues if i['severity'] == '🟡 MÉDIO')} |
| Baixos | {sum(1 for i in self.issues if i['severity'] == '🟢 BAIXO')} |
| API Status | {self.api_status.get('health', 'N/A')} |

---

## 📁 Status das Telas

"""
        
        # Status das telas
        for filename, specs in EXPECTED_SCREENS.items():
            exists = (FRONTEND_DIR / filename).exists()
            status = "✅" if exists else "❌"
            required = "(obrigatória)" if specs["required"] else "(opcional)"
            report += f"| {status} | {filename} | {specs['title']} | {required} |\n"
        
        report += "\n---\n\n"
        
        # Itens OK
        if self.ok_items:
            report += "## ✅ Itens Verificados com Sucesso\n\n"
            for item in self.ok_items:
                report += f"- **{item['screen']}:** {item['description']}\n"
            report += "\n---\n\n"
        
        # Problemas Críticos
        criticals = [i for i in self.issues if i['severity'] == '🔴 CRÍTICO']
        if criticals:
            report += "## 🔴 Problemas Críticos (Corrigir Imediatamente)\n\n"
            for issue in criticals:
                report += f"- **{issue['screen']}:** {issue['description']}\n"
            report += "\n---\n\n"
        
        # Problemas Médios
        mediums = [i for i in self.issues if i['severity'] == '🟡 MÉDIO']
        if mediums:
            report += "## 🟡 Problemas Médios (Corrigir Esta Semana)\n\n"
            for issue in mediums:
                report += f"- **{issue['screen']}:** {issue['description']}\n"
            report += "\n---\n\n"
        
        # Problemas Baixos
        lows = [i for i in self.issues if i['severity'] == '🟢 BAIXO']
        if lows:
            report += "## 🟢 Problemas Baixos (Quando Possível)\n\n"
            for issue in lows:
                report += f"- **{issue['screen']}:** {issue['description']}\n"
            report += "\n---\n\n"
        
        # Recomendações
        report += """## 📝 Recomendações Automáticas

"""
        
        # Recomendações baseadas nos problemas
        if any(i['screen'] == 'missions.html' for i in criticals):
            report += """### 1. Criar missions.html
```html
<!-- Estrutura sugerida -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <title>Dunder Mifflin - Missões</title>
    <!-- Mesmas fontes e CSS do index.html -->
</head>
<body>
    <div class="window">
        <div class="window-title"><h1>📋 MISSÕES</h1></div>
        <div class="window-content">
            <!-- Lista de missões com filtros -->
            <div id="missions-list"></div>
        </div>
    </div>
    <script>
        // Carregar de /api/missions
        fetch(`${API}/missions`).then(r => r.json()).then(data => {
            // Renderizar lista
        });
    </script>
</body>
</html>
```

"""
        
        if any(i['screen'] == 'files.html' for i in criticals):
            report += """### 2. Criar files.html
Listar arquivos gerados em `~/.openclaw/workspace/studio/projects/dunder_mifflin/`

"""
        
        report += f"""### 3. Padronizar Design
- Usar sempre: `{', '.join(EXPECTED_FONTS)}`
- Cores Win95: `{', '.join(WIN95_VARS.keys())}`
- Evitar Tailwind em novas telas

---

*Relatório gerado automaticamente em {now}*
"""
        
        return report
    
    def run(self):
        """Executa auditoria completa"""
        print("🔍 Iniciando auditoria de interface...")
        
        # Testa API
        print("📡 Testando API...")
        self.test_api_health()
        
        # Verifica cada tela
        print("📁 Verificando telas...")
        for filename in EXPECTED_SCREENS:
            if self.check_screen_exists(filename):
                print(f"  ✓ Analisando {filename}...")
                self.analyze_design_consistency(filename)
                self.check_api_integration(filename)
                self.check_navigation(filename)
            else:
                print(f"  ✗ {filename} não existe")
        
        # Gera relatório
        print("📝 Gerando relatório...")
        report = self.generate_report()
        
        # Salva relatório
        output_file = OUTPUT_DIR / "auditoria-interface-automatica.md"
        output_file.write_text(report, encoding='utf-8')
        
        # Resumo
        print(f"\n{'='*50}")
        print(f"✅ Auditoria completa!")
        print(f"📄 Relatório salvo em: {output_file}")
        print(f"📊 Resumo:")
        print(f"   - Telas existentes: {sum(1 for s in EXPECTED_SCREENS if (FRONTEND_DIR / s).exists())}/{len(EXPECTED_SCREENS)}")
        print(f"   - Problemas críticos: {sum(1 for i in self.issues if i['severity'] == '🔴 CRÍTICO')}")
        print(f"   - Problemas médios: {sum(1 for i in self.issues if i['severity'] == '🟡 MÉDIO')}")
        print(f"   - Problemas baixos: {sum(1 for i in self.issues if i['severity'] == '🟢 BAIXO')}")
        print(f"{'='*50}")
        
        return report


if __name__ == "__main__":
    auditor = InterfaceAuditor()
    auditor.run()
