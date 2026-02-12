#!/usr/bin/env python3
"""
Ralph Swarm - RAG Memory Module v1.0
Sistema de memória compartilhada para agents do swarm
Integrado ao swarm v5 existente
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

# Database path (usa o mesmo do swarm)
SWARM_DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"
RAG_DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/swarm/rag_memory.db"

@dataclass
class RAGExample:
    """Exemplo aprovado de output de agent"""
    id: str
    task_type: str  # analysis, code, content, research, etc
    project: str
    task: str
    output: str
    approved_by: str
    quality_score: int  # 1-5
    tags: List[str]
    created_at: str
    agent_slug: Optional[str] = None
    task_id: Optional[str] = None

@dataclass
class RAGMistake:
    """Erro corrigido para aprendizado"""
    id: str
    task_type: str
    project: str
    task: str
    rejected_output: str
    feedback: str
    correction: str
    rejected_by: str
    tags: List[str]
    created_at: str
    agent_slug: Optional[str] = None
    task_id: Optional[str] = None

class SwarmRAGMemory:
    """
    Sistema RAG para o Ralph Swarm.
    
    Uso:
        from swarm.rag_memory import SwarmRAGMemory
        
        rag = SwarmRAGMemory()
        
        # Buscar exemplos antes de executar
        examples = rag.search_examples("analysis", "meu-projeto", "analisar conversão")
        
        # Salvar após aprovação
        rag.save_example(...)
        
        # Salvar erro após reprovação
        rag.save_mistake(...)
    """
    
    def __init__(self, db_path: Path = RAG_DB_PATH):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """Garante que banco e tabelas existem"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # Tabela de exemplos aprovados
        conn.execute("""
            CREATE TABLE IF NOT EXISTS examples (
                id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                project TEXT NOT NULL,
                task TEXT NOT NULL,
                output TEXT NOT NULL,
                approved_by TEXT NOT NULL,
                quality_score INTEGER DEFAULT 5,
                tags TEXT,  -- JSON array
                created_at TEXT NOT NULL,
                agent_slug TEXT,
                task_id TEXT
            )
        """)
        
        # Tabela de erros/mistakes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                project TEXT NOT NULL,
                task TEXT NOT NULL,
                rejected_output TEXT NOT NULL,
                feedback TEXT NOT NULL,
                correction TEXT NOT NULL,
                rejected_by TEXT NOT NULL,
                tags TEXT,  -- JSON array
                created_at TEXT NOT NULL,
                agent_slug TEXT,
                task_id TEXT
            )
        """)
        
        # Índices
        conn.execute("CREATE INDEX IF NOT EXISTS idx_examples_project ON examples(project)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_examples_task_type ON examples(task_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mistakes_project ON mistakes(project)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mistakes_task_type ON mistakes(task_type)")
        
        conn.commit()
        conn.close()
    
    def _generate_id(self) -> str:
        """Gera ID único"""
        content = f"{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def save_example(self, task_type: str, project: str, task: str,
                     output: str, approved_by: str, quality_score: int = 5,
                     tags: List[str] = None, agent_slug: str = None,
                     task_id: str = None) -> str:
        """
        Salva exemplo aprovado.
        
        Returns:
            ID do exemplo salvo
        """
        entry_id = self._generate_id()
        tags = tags or []
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO examples 
            (id, task_type, project, task, output, approved_by, quality_score, tags, created_at, agent_slug, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, task_type, project, task, output, approved_by, quality_score,
            json.dumps(tags), timestamp, agent_slug, task_id
        ))
        conn.commit()
        conn.close()
        
        return entry_id
    
    def save_mistake(self, task_type: str, project: str, task: str,
                     rejected_output: str, feedback: str, correction: str,
                     rejected_by: str, tags: List[str] = None,
                     agent_slug: str = None, task_id: str = None) -> str:
        """
        Salva erro corrigido.
        
        Returns:
            ID do erro salvo
        """
        entry_id = self._generate_id()
        tags = tags or []
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO mistakes 
            (id, task_type, project, task, rejected_output, feedback, correction, rejected_by, tags, created_at, agent_slug, task_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, task_type, project, task, rejected_output, feedback, correction,
            rejected_by, json.dumps(tags), timestamp, agent_slug, task_id
        ))
        conn.commit()
        conn.close()
        
        return entry_id
    
    def search_examples(self, task_type: str, project: str, query: str,
                        limit: int = 3) -> List[Dict]:
        """
        Busca exemplos similares.
        
        Args:
            task_type: Tipo de task (analysis, code, etc)
            project: Nome do projeto
            query: Texto da task atual (para matching simples)
            limit: Quantos exemplos retornar
            
        Returns:
            Lista de exemplos ordenados por relevância
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Busca simples: mesma task_type, ordena por qualidade e data
        cursor = conn.execute("""
            SELECT * FROM examples 
            WHERE task_type = ? 
            AND (project = ? OR project = 'global')
            ORDER BY quality_score DESC, created_at DESC
            LIMIT ?
        """, (task_type, project, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            data = dict(row)
            data['tags'] = json.loads(data.get('tags', '[]'))
            results.append(data)
        
        return results
    
    def get_mistakes(self, task_type: str, project: str,
                     limit: int = 5) -> List[Dict]:
        """
        Recupera erros comuns para evitar.
        
        Returns:
            Lista de erros com feedback e correção
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT task, feedback, correction, tags FROM mistakes 
            WHERE task_type = ? 
            AND (project = ? OR project = 'global')
            ORDER BY created_at DESC
            LIMIT ?
        """, (task_type, project, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            data = dict(row)
            data['tags'] = json.loads(data.get('tags', '[]'))
            results.append(data)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        conn = sqlite3.connect(self.db_path)
        
        # Contagem de exemplos
        cursor = conn.execute("SELECT COUNT(*) FROM examples")
        examples_count = cursor.fetchone()[0]
        
        # Contagem de erros
        cursor = conn.execute("SELECT COUNT(*) FROM mistakes")
        mistakes_count = cursor.fetchone()[0]
        
        # Qualidade média
        cursor = conn.execute("SELECT AVG(quality_score) FROM examples")
        avg_quality = cursor.fetchone()[0] or 0
        
        # Por task_type
        cursor = conn.execute("""
            SELECT task_type, COUNT(*) as count 
            FROM examples 
            GROUP BY task_type
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'examples': examples_count,
            'mistakes': mistakes_count,
            'avg_quality': round(avg_quality, 1),
            'by_task_type': by_type
        }
    
    def format_context_for_prompt(self, examples: List[Dict],
                                  mistakes: List[Dict]) -> str:
        """
        Formata contexto RAG para inclusão no prompt.
        
        Returns:
            Texto formatado para adicionar ao prompt do agent
        """
        sections = []
        
        if examples:
            sections.append("## 📚 Exemplos de Qualidade (Aprovados)\n")
            for i, ex in enumerate(examples[:2], 1):
                output_preview = ex['output'][:400] + "..." if len(ex['output']) > 400 else ex['output']
                sections.append(f"### Exemplo {i} (⭐ {ex['quality_score']}/5)")
                sections.append(f"Task: {ex['task']}")
                sections.append(f"Output:\n{output_preview}\n")
        
        if mistakes:
            sections.append("\n## ⚠️ Erros a Evitar\n")
            for i, m in enumerate(mistakes[:3], 1):
                sections.append(f"{i}. **{m['feedback']}**")
                sections.append(f"   Correção: {m['correction'][:100]}...")
        
        if not sections:
            return ""
        
        return "\n".join([
            "\n" + "="*50,
            "CONTEXTO DE MEMÓRIA DO SWARM",
            "="*50,
            "\n".join(sections),
            "="*50 + "\n"
        ])

# Singleton instance
_rag_instance = None

def get_rag_memory() -> SwarmRAGMemory:
    """Retorna instância singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = SwarmRAGMemory()
    return _rag_instance


# Função helper para facilitar uso nos agents
def get_context_for_task(task_type: str, project: str, task: str) -> str:
    """
    Busca e formata contexto RAG de uma vez.
    
    Uso em agent_brain.py:
        from swarm.rag_memory import get_context_for_task
        
        rag_context = get_context_for_task("analysis", "meu-proj", task_desc)
        prompt = f"{rag_context}\n\nTask: {task}"
    """
    rag = get_rag_memory()
    examples = rag.search_examples(task_type, project, task)
    mistakes = rag.get_mistakes(task_type, project)
    return rag.format_context_for_prompt(examples, mistakes)


if __name__ == "__main__":
    # Teste
    print("🧪 Testando SwarmRAGMemory...")
    
    rag = get_rag_memory()
    
    # Salva exemplo de teste
    ex_id = rag.save_example(
        task_type="analysis",
        project="test",
        task="Analisar métricas de conversão",
        output="# Análise\n- Conversão: 5.2%\n- Recomendação: Melhorar CTA",
        approved_by="test",
        quality_score=5,
        tags=["conversao", "landing-page"]
    )
    print(f"✅ Exemplo salvo: {ex_id}")
    
    # Salva erro de teste
    err_id = rag.save_mistake(
        task_type="analysis",
        project="test",
        task="Análise superficial",
        rejected_output="Precisa melhorar",
        feedback="Faltou dados específicos",
        correction="Incluir métricas e benchmarks",
        rejected_by="test",
        tags=["superficial"]
    )
    print(f"✅ Erro salvo: {err_id}")
    
    # Busca
    examples = rag.search_examples("analysis", "test", "conversão")
    mistakes = rag.get_mistakes("analysis", "test")
    print(f"✅ Encontrados: {len(examples)} exemplos, {len(mistakes)} erros")
    
    # Stats
    stats = rag.get_stats()
    print(f"✅ Stats: {stats}")
    
    print("\n🎉 Tudo funcionando!")
