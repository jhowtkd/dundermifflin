#!/usr/bin/env python3
"""
Ralph Swarm - Advanced Synthesis Engine v5.0
Síntese inteligente de resultados com qualidade e coerência
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))
from ralph_swarm_core import ChannelSystem
sys.path.insert(0, str(Path(__file__).parent))
from agent_brain import AgentBrain

class SynthesisQuality(Enum):
    """Níveis de qualidade da síntese"""
    DRAFT = "draft"           # Rascunho rápido
    STANDARD = "standard"     # Padrão
    POLISHED = "polished"     # Polido e revisado
    EXECUTIVE = "executive"   # Nível executivo

@dataclass
class SynthesisConfig:
    """Configuração de síntese"""
    quality: SynthesisQuality = SynthesisQuality.STANDARD
    max_length: int = 2000
    include_action_items: bool = True
    include_metrics: bool = True
    tone: str = "professional"  # professional, casual, technical
    format: str = "markdown"    # markdown, json, html

@dataclass
class AgentOutput:
    """Output de um agent"""
    agent_slug: str
    agent_name: str
    role: str
    content: str
    tokens_used: int = 0
    confidence: float = 1.0

@dataclass
class SynthesisResult:
    """Resultado da síntese"""
    title: str
    summary: str
    key_points: List[str]
    details: Dict[str, str]
    action_items: List[str]
    metrics: Dict[str, any]
    quality_score: float
    completion_status: str
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'summary': self.summary,
            'key_points': self.key_points,
            'details': self.details,
            'action_items': self.action_items,
            'metrics': self.metrics,
            'quality_score': self.quality_score,
            'completion_status': self.completion_status
        }

class SynthesisEngine:
    """
    Engine avançado de síntese.
    Transforma outputs fragmentados em entregas coesas e profissionais.
    """
    
    def __init__(self):
        self.channels = ChannelSystem()
        self.ralph_brain = AgentBrain('ralph')
    
    def extract_key_information(self, outputs: List[AgentOutput]) -> Dict:
        """
        Extrai informações chave dos outputs dos agents.
        """
        extracted = {
            'research_findings': [],
            'technical_deliverables': [],
            'content_created': [],
            'analytics_insights': [],
            'monitoring_alerts': []
        }
        
        for output in outputs:
            content_lower = output.content.lower()
            
            # Classificar por tipo de conteúdo
            if output.role == 'find' or 'research' in content_lower:
                extracted['research_findings'].append({
                    'agent': output.agent_name,
                    'content': output.content
                })
            
            elif output.role == 'build' or any(kw in content_lower for kw in ['código', 'build', 'implementado']):
                extracted['technical_deliverables'].append({
                    'agent': output.agent_name,
                    'content': output.content
                })
            
            elif output.role == 'create' or any(kw in content_lower for kw in ['copy', 'headline', 'escrito']):
                extracted['content_created'].append({
                    'agent': output.agent_name,
                    'content': output.content
                })
            
            elif output.role == 'track':
                extracted['analytics_insights'].append({
                    'agent': output.agent_name,
                    'content': output.content
                })
            
            elif output.role == 'watch':
                extracted['monitoring_alerts'].append({
                    'agent': output.agent_name,
                    'content': output.content
                })
        
        return extracted
    
    def generate_title(self, original_task: str, outputs: List[AgentOutput]) -> str:
        """Gera título apropriado para a entrega"""
        # Simplificar: usar primeira parte da tarefa
        task_parts = original_task.split()
        key_words = [w for w in task_parts[:5] if len(w) > 3]
        
        if 'landing page' in original_task.lower():
            return "Landing Page Completa - Entrega Final"
        elif 'research' in original_task.lower() or 'concorrentes' in original_task.lower():
            return "Research de Mercado - Análise Completa"
        elif 'copy' in original_task.lower():
            return "Copy e Conteúdo - Entrega Final"
        else:
            return f"Entrega: {' '.join(key_words)}"
    
    def synthesize(self, 
                   original_task: str, 
                   outputs: List[AgentOutput],
                   config: Optional[SynthesisConfig] = None) -> SynthesisResult:
        """
        Síntese principal: consolida outputs em entrega final.
        
        Args:
            original_task: Descrição original da tarefa
            outputs: Lista de outputs dos agents
            config: Configuração de síntese
            
        Returns:
            SynthesisResult com entrega consolidada
        """
        if config is None:
            config = SynthesisConfig()
        
        # 1. Extrair informações estruturadas
        extracted = self.extract_key_information(outputs)
        
        # 2. Gerar título
        title = self.generate_title(original_task, outputs)
        
        # 3. Criar prompt de síntese para Ralph
        synthesis_prompt = self._create_synthesis_prompt(
            original_task, outputs, extracted, config
        )
        
        # 4. Ralph executa síntese
        ralph_response = self.ralph_brain.think(
            task=synthesis_prompt,
            output_format="Crie uma entrega final completa, profissional e pronta para uso."
        )
        
        # 5. Parse da resposta de Ralph
        parsed = self._parse_synthesis_response(ralph_response)
        
        # 6. Calcular quality score
        quality_score = self._calculate_quality_score(outputs, parsed)
        
        # 7. Extrair action items se necessário
        action_items = []
        if config.include_action_items:
            action_items = self._extract_action_items(ralph_response)
        
        # 8. Extrair métricas se necessário
        metrics = {}
        if config.include_metrics:
            metrics = self._extract_metrics(outputs)
        
        return SynthesisResult(
            title=title,
            summary=parsed.get('summary', ''),
            key_points=parsed.get('key_points', []),
            details=parsed.get('details', {}),
            action_items=action_items,
            metrics=metrics,
            quality_score=quality_score,
            completion_status='completed'
        )
    
    def _create_synthesis_prompt(self, 
                                  task: str, 
                                  outputs: List[AgentOutput],
                                  extracted: Dict,
                                  config: SynthesisConfig) -> str:
        """Cria prompt detalhado para síntese"""
        
        # Formatar outputs
        outputs_text = "\n\n".join([
            f"### {out.agent_name} ({out.role})\n{out.content[:1000]}"
            for out in outputs
        ])
        
        quality_instructions = {
            SynthesisQuality.DRAFT: "Crie um rascunho rápido e direto.",
            SynthesisQuality.STANDARD: "Crie uma entrega padrão, bem estruturada.",
            SynthesisQuality.POLISHED: "Crie uma entrega polida e revisada, atenção aos detalhes.",
            SynthesisQuality.EXECUTIVE: "Crie um resumo executivo de alto nível, focado em decisões."
        }
        
        prompt = f"""Você é Ralph, o Coordenador. Sua tarefa é sintetizar outputs de múltiplos agents em uma entrega final coesa e profissional.

## TAREFA ORIGINAL
{task}

## OUTPUTS DOS AGENTS
{outputs_text}

## INSTRUÇÕES DE SÍNTESE
{quality_instructions.get(config.quality, quality_instructions[SynthesisQuality.STANDARD])}

Tom: {config.tone}
Formato: {config.format}
Comprimento máximo: {config.max_length} caracteres

## ESTRUTURA DESEJADA
1. **Resumo Executivo** (2-3 frases com o essencial)
2. **Pontos Principais** (3-5 bullets com insights chave)
3. **Detalhes por Área**:
   - Research/Mercado
   - Técnico/Implementação
   - Conteúdo/Copy
   - Analytics (se houver)
4. **Próximos Passos** (2-3 ações concretas)

## REGRAS
- Conecte os pontos entre diferentes agents
- Elimine redundâncias
- Destaque insights acionáveis
- Mantenha tom {config.tone}
- SEMPRE termine com \u003cRALPH_COMPLETE\u003e

Execute a síntese agora:"""
        
        return prompt
    
    def _parse_synthesis_response(self, response: str) -> Dict:
        """Parse da resposta de Ralph em estrutura"""
        parsed = {
            'summary': '',
            'key_points': [],
            'details': {}
        }
        
        # Extrair resumo (primeiras linhas até primeiro ## ou lista)
        lines = response.split('\n')
        summary_lines = []
        for line in lines[:10]:
            if line.startswith('##') or line.startswith('**'):
                break
            if line.strip():
                summary_lines.append(line.strip())
        parsed['summary'] = ' '.join(summary_lines)[:500]
        
        # Extrair key points (bullets)
        key_points = []
        for line in lines:
            if line.strip().startswith(('•', '-', '*')) and len(line) > 10:
                key_points.append(line.strip()[2:].strip())
        parsed['key_points'] = key_points[:5]
        
        # Extrair seções de detalhes
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('## '):
                if current_section:
                    parsed['details'][current_section] = '\n'.join(current_content)
                current_section = line[3:].strip().lower()
                current_content = []
            elif current_section and line.strip():
                current_content.append(line)
        
        if current_section:
            parsed['details'][current_section] = '\n'.join(current_content)
        
        return parsed
    
    def _calculate_quality_score(self, outputs: List[AgentOutput], parsed: Dict) -> float:
        """Calcula score de qualidade da síntese"""
        score = 0.0
        
        # Base: número de agents que contribuíram
        score += min(len(outputs) * 10, 30)
        
        # Tem resumo?
        if parsed.get('summary') and len(parsed['summary']) > 50:
            score += 20
        
        # Tem key points?
        if len(parsed.get('key_points', [])) >= 3:
            score += 20
        
        # Tem detalhes?
        if len(parsed.get('details', {})) >= 2:
            score += 20
        
        # Bônus por completude
        if len(outputs) >= 3:
            score += 10
        
        return min(score, 100)
    
    def _extract_action_items(self, response: str) -> List[str]:
        """Extrai itens de ação da resposta"""
        actions = []
        
        # Procurar por seção de próximos passos/ações
        lines = response.split('\n')
        in_action_section = False
        
        for line in lines:
            lower = line.lower()
            if any(kw in lower for kw in ['próximos passos', 'next steps', 'action items', 'ações']):
                in_action_section = True
                continue
            
            if in_action_section:
                if line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')):
                    action = line.strip()
                    # Limpar marcadores
                    action = re.sub(r'^[•\-\*\d\.\)\s]+', '', action)
                    if len(action) > 10:
                        actions.append(action)
                elif line.startswith('##'):
                    break
        
        return actions[:5]
    
    def _extract_metrics(self, outputs: List[AgentOutput]) -> Dict:
        """Extrai métricas dos outputs"""
        metrics = {
            'agents_contributed': len(outputs),
            'total_tokens': sum(out.tokens_used for out in outputs),
            'avg_confidence': sum(out.confidence for out in outputs) / len(outputs) if outputs else 0,
            'coverage': {
                'research': any(o.role == 'find' for o in outputs),
                'technical': any(o.role == 'build' for o in outputs),
                'content': any(o.role == 'create' for o in outputs),
                'analytics': any(o.role == 'track' for o in outputs)
            }
        }
        
        return metrics
    
    def format_for_delivery(self, result: SynthesisResult, format_type: str = 'markdown') -> str:
        """Formata resultado para entrega"""
        
        if format_type == 'json':
            return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        
        if format_type == 'html':
            return self._format_html(result)
        
        # Markdown (default)
        return self._format_markdown(result)
    
    def _format_markdown(self, result: SynthesisResult) -> str:
        """Formata como markdown"""
        lines = [
            f"# {result.title}",
            "",
            f"**Score de Qualidade:** {result.quality_score:.0f}/100",
            f"**Status:** {result.completion_status}",
            "",
            "## Resumo Executivo",
            result.summary,
            "",
            "## Pontos Principais",
        ]
        
        for point in result.key_points:
            lines.append(f"• {point}")
        
        if result.details:
            lines.extend(["", "## Detalhes"])
            for section, content in result.details.items():
                lines.extend([f"\n### {section.title()}", content])
        
        if result.action_items:
            lines.extend(["", "## Próximos Passos"])
            for i, action in enumerate(result.action_items, 1):
                lines.append(f"{i}. {action}")
        
        if result.metrics:
            lines.extend(["", "## Métricas"])
            lines.append(f"• Agents: {result.metrics.get('agents_contributed', 0)}")
            lines.append(f"• Tokens: {result.metrics.get('total_tokens', 0)}")
            lines.append(f"• Confiança: {result.metrics.get('avg_confidence', 0):.0%}")
        
        return '\n'.join(lines)
    
    def _format_html(self, result: SynthesisResult) -> str:
        """Formata como HTML"""
        # Simplified HTML output
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{result.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; }}
        .meta {{ color: #999; font-size: 0.9em; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        ul {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>{result.title}</h1>
    <p class="meta">Quality Score: {result.quality_score:.0f}/100 | Status: {result.completion_status}</p>
    
    <h2>Resumo Executivo</h2>
    <div class="summary">{result.summary}</div>
    
    <h2>Pontos Principais</h2>
    <ul>
        {''.join(f'<li>{p}</li>' for p in result.key_points)}
    </ul>
"""
        
        if result.action_items:
            html += f"""
    <h2>Próximos Passos</h2>
    <ol>
        {''.join(f'<li>{a}</li>' for a in result.action_items)}
    </ol>
"""
        
        html += """
</body>
</html>
"""
        return html


# Teste
if __name__ == '__main__':
    print("🧠 Advanced Synthesis Engine - Teste")
    print("=" * 60)
    
    engine = SynthesisEngine()
    
    # Simular outputs de agents
    outputs = [
        AgentOutput(
            agent_slug='scout',
            agent_name='Scout',
            role='find',
            content="🔍 RESEARCH RESULTS\n\nEncontrados 15 concorrentes. Principais: Notion ($10/mês), ClickUp ($5/mês), Asana ($11/mês). Tendência: precificação freemium."
        ),
        AgentOutput(
            agent_slug='maya',
            agent_name='Maya',
            role='create',
            content="📝 COPY RESULTS\n\nHeadlines: 'Transforme sua produtividade em 30 dias', 'O sistema que 10,000+ profissionais usam'. CTAs: 'Comece grátis hoje'."
        ),
        AgentOutput(
            agent_slug='max',
            agent_name='Max',
            role='build',
            content="🛠️ BUILD RESULTS\n\nLanding page scaffold criado: index.html, styles.css, script.js. Features: hero section, pricing cards, FAQ."
        )
    ]
    
    print("\n1️⃣ Testando síntese:")
    result = engine.synthesize(
        original_task="Criar landing page para SaaS de produtividade",
        outputs=outputs,
        config=SynthesisConfig(quality=SynthesisQuality.STANDARD)
    )
    
    print(f"   ✅ Título: {result.title}")
    print(f"   📊 Quality Score: {result.quality_score:.0f}/100")
    print(f"   📝 Key Points: {len(result.key_points)}")
    print(f"   ✅ Action Items: {len(result.action_items)}")
    
    print("\n2️⃣ Formatando para entrega:")
    markdown = engine.format_for_delivery(result, 'markdown')
    print(f"   ✅ Markdown gerado: {len(markdown)} caracteres")
    print(f"   \n   Preview:\n   {markdown[:400]}...")
    
    print("\n" + "=" * 60)
    print("✅ Testes completados!")
