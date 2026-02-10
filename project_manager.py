#!/usr/bin/env python3
"""
Project Manager para Dunder Mifflin
Gerencia estrutura de pastas, Git e GitHub para projetos
"""

import os
import json
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configurações
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace" / "projects"
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

class ProjectManager:
    """Gerencia projetos, repositórios e integração Git/GitHub"""
    
    def __init__(self):
        self.workspace = WORKSPACE_DIR
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def create_project(self, name: str, github_url: Optional[str] = None) -> Dict:
        """Cria estrutura de pasta para novo projeto"""
        
        # Sanitiza nome do projeto
        project_slug = name.lower().replace(" ", "-").replace("_", "-")
        project_path = self.workspace / project_slug
        
        if project_path.exists():
            return {
                "status": "error",
                "message": f"Projeto '{name}' já existe"
            }
        
        # Cria estrutura de pastas
        (project_path / "src").mkdir(parents=True)
        (project_path / "docs").mkdir()
        (project_path / "tests").mkdir()
        
        # README inicial
        readme_content = f"""# {name}

Projeto criado em {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Estrutura

```
{project_slug}/
├── src/           # Código fonte
├── docs/          # Documentação
├── tests/         # Testes
└── README.md      # Este arquivo
```

## Desenvolvimento

Agentes do Dunder Mifflin trabalham neste projeto.
"""
        
        (project_path / "README.md").write_text(readme_content)
        
        # Se tiver URL do GitHub, clona
        if github_url:
            result = self._clone_repo(github_url, project_path)
            if result["status"] == "error":
                return result
        
        # Salva no banco
        self._save_project_to_db(project_slug, name, str(project_path), github_url)
        
        return {
            "status": "success",
            "message": f"Projeto '{name}' criado com sucesso",
            "path": str(project_path),
            "slug": project_slug
        }
    
    def _clone_repo(self, github_url: str, project_path: Path) -> Dict:
        """Clona repositório do GitHub"""
        try:
            # Remove pasta vazia criada
            import shutil
            shutil.rmtree(project_path)
            
            # Clona repo
            cmd = ["git", "clone", github_url, str(project_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Erro ao clonar: {result.stderr}"
                }
            
            return {"status": "success"}
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao clonar: {str(e)}"
            }
    
    def _save_project_to_db(self, slug: str, name: str, path: str, github_url: Optional[str]):
        """Salva projeto no banco de dados"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Cria tabela se não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                github_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            INSERT OR REPLACE INTO projects (slug, name, path, github_url)
            VALUES (?, ?, ?, ?)
        """, (slug, name, path, github_url))
        
        conn.commit()
        conn.close()
    
    def get_project(self, slug: str) -> Optional[Dict]:
        """Busca projeto pelo slug"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM projects WHERE slug = ?", (slug,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "slug": row[1],
                "name": row[2],
                "path": row[3],
                "github_url": row[4],
                "created_at": row[5]
            }
        return None
    
    def list_projects(self) -> List[Dict]:
        """Lista todos os projetos"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "slug": row[1],
                "name": row[2],
                "path": row[3],
                "github_url": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

class GitManager:
    """Gerencia operações Git e GitHub"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.github_token = os.getenv("GITHUB_TOKEN", "")
    
    def exec_git(self, args: List[str], timeout: int = 30) -> Dict:
        """Executa comando git no projeto"""
        try:
            cmd = ["git"] + args
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def checkout_branch(self, branch_name: str) -> Dict:
        """Cria e faz checkout de nova branch"""
        # Tenta criar branch
        result = self.exec_git(["checkout", "-b", branch_name])
        
        if result["status"] == "error":
            # Branch pode já existir, tenta fazer checkout
            result = self.exec_git(["checkout", branch_name])
        
        return result
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> Dict:
        """Adiciona e commita alterações"""
        # Adiciona arquivos
        if files:
            for f in files:
                self.exec_git(["add", f])
        else:
            self.exec_git(["add", "."])
        
        # Commit
        return self.exec_git(["commit", "-m", message])
    
    def push_branch(self, branch: str, remote: str = "origin") -> Dict:
        """Faz push da branch"""
        return self.exec_git(["push", "-u", remote, branch])
    
    def get_status(self) -> Dict:
        """Retorna status do git"""
        status = self.exec_git(["status", "--short"])
        branch = self.exec_git(["branch", "--show-current"])
        
        return {
            "branch": branch["stdout"].strip() if branch["status"] == "success" else "unknown",
            "has_changes": len(status["stdout"]) > 0,
            "files_changed": status["stdout"].split("\n") if status["stdout"] else []
        }
    
    def create_pull_request(self, title: str, body: str, base: str = "main") -> Dict:
        """Cria Pull Request via GitHub CLI (requer gh instalado)"""
        try:
            cmd = [
                "gh", "pr", "create",
                "--title", title,
                "--body", body,
                "--base", base
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "url": result.stdout.strip() if result.returncode == 0 else None,
                "message": result.stderr if result.returncode != 0 else None
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "message": "GitHub CLI (gh) não instalado"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

def main():
    """Teste do módulo"""
    pm = ProjectManager()
    
    # Cria projeto de teste
    result = pm.create_project("Meu Projeto Teste")
    print(json.dumps(result, indent=2))
    
    # Lista projetos
    projects = pm.list_projects()
    print(f"\nProjetos: {len(projects)}")

if __name__ == "__main__":
    main()
