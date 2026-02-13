#!/usr/bin/env python3
"""
Ralph Iteration Engine - Fase 2
Motor de iteração contínua para execução de loops
"""

import os
import re
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime

# Importar loop_manager e llm_client
from loop_manager import LoopManager, LoopStatus, RalphLoop, LoopIteration
from llm_client import LLMClient, LLMResponse


@dataclass
class IterationResult:
    """Resultado de uma iteração"""
    success: bool
    response: str
    tokens_in: int
    tokens_out: int
    duration_seconds: float
    completed: bool  # Se detectou RALPH_COMPLETE
    error: Optional[str] = None


@dataclass
class EngineConfig:
    """Configuração do motor de iteração"""
    model: str = "kimi-coding/k2p5"  # Modelo padrão
    completion_promise: str = "RALPH_COMPLETE"
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout_seconds: int = 120
    cost_per_1k_in: float = 0.001  # Kimi K2
    cost_per_1k_out: float = 0.003  # Kimi K2


class PromptBuilder:
    """Construtor de prompts para iterações"""
    
    def __init__(self, completion_promise: str = "RALPH_COMPLETE"):
        self.completion_promise = completion_promise
    
    def build_iteration_prompt(
        self,
        task_description: str,
        agent_slug: str,
        iteration_number: int,
        max_iterations: int,
        previous_iterations: List[Dict],
        agent_personality: Optional[str] = None
    ) -> str:
        """
        Constrói o prompt para uma iteração.
        
        Args:
            task_description: Descrição da tarefa original
            agent_slug: Slug do agente executando
            iteration_number: Número da iteração atual
            max_iterations: Máximo de iterações permitidas
            previous_iterations: Lista de iterações anteriores
            agent_personality: Personalidade do agente (opcional)
            
        Returns:
            Prompt formatado
        """
        # Cabeçalho
        prompt = f"""# Iteração {iteration_number} de {max_iterations}

## Tarefa Original
{task_description}

"""
        
        # Personalidade do agente (se disponível)
        if agent_personality:
            prompt += f"""## Sua Personalidade
{agent_personality}

"""
        
        # Progresso anterior
        if previous_iterations:
            prompt += """## Progresso Anterior
"""
            for i, prev in enumerate(previous_iterations, 1):
                prompt += f"""
### Iteração {i}
**O que foi feito:**
{prev.get('summary', 'N/A')}

**Resultado:**
{prev.get('result', 'N/A')}
"""
        else:
            prompt += """## Progresso Anterior
Esta é a primeira iteração. Analise a tarefa e comece o trabalho.

"""
        
        # Instruções
        prompt += f"""## Instruções para esta Iteração

1. **Analise** o progresso anterior (se houver)
2. **Execute** o PRÓXIMO passo lógico da tarefa
   - Não tente fazer tudo de uma vez
   - Avance incrementalmente
3. **Documente** o que foi feito nesta iteração
4. **Avalie** se a tarefa está completa
5. **Se completa**, inclua no final: `{self.completion_promise}`

## Regras Importantes

- ✅ Não reinvente o que já foi feito
- ✅ Se encontrar erro, corrija e continue
- ✅ Se travar por mais de 3 iterações, documente o bloqueio
- ✅ Sempre mantenha o foco na tarefa original
- ✅ Output `{self.completion_promise}` apenas quando REALMENTE completo

## Formato da Resposta

**O que foi feito nesta iteração:**
[Descreva o trabalho realizado]

**Próximos passos:**
[O que falta fazer ou 'Tarefa completa']

**Métricas:**
- Estimativa de tokens in: [número]
- Estimativa de tokens out: [número]

Execute agora:
"""
        
        return prompt
    
    def build_first_iteration_prompt(
        self,
        task_description: str,
        agent_slug: str,
        max_iterations: int,
        agent_personality: Optional[str] = None
    ) -> str:
        """Prompt especial para primeira iteração"""
        return self.build_iteration_prompt(
            task_description=task_description,
            agent_slug=agent_slug,
            iteration_number=1,
            max_iterations=max_iterations,
            previous_iterations=[],
            agent_personality=agent_personality
        )


class CompletionDetector:
    """Detector de completion em respostas"""
    
    def __init__(self, completion_promise: str = "RALPH_COMPLETE"):
        self.completion_promise = completion_promise
        # Padrões que indicam completion
        self.completion_patterns = [
            re.compile(re.escape(completion_promise), re.IGNORECASE),
            re.compile(r'tarefa\s+(completada?|finalizada?|concluída?)', re.IGNORECASE),
            re.compile(r'loop\s+(completado|finalizado|concluído)', re.IGNORECASE),
        ]
    
    def detect(self, response: str) -> bool:
        """
        Detecta se a resposta indica completion.
        
        Returns:
            True se detectou completion
        """
        for pattern in self.completion_patterns:
            if pattern.search(response):
                return True
        return False
    
    def extract_summary(self, response: str) -> str:
        """
        Extrai um resumo da resposta (primeiros 500 chars).
        
        Returns:
            Resumo truncado
        """
        lines = response.strip().split('\n')
        # Pegar primeiras linhas relevantes
        summary_lines = []
        for line in lines:
            if line.strip() and not line.startswith('---'):
                summary_lines.append(line)
            if len(summary_lines) >= 5:
                break
        
        summary = ' '.join(summary_lines)
        if len(summary) > 500:
            summary = summary[:497] + '...'
        
        return summary


class IterationEngine:
    """
    Motor de iteração do Ralph.
    Executa loops de forma assíncrona com callbacks.
    """
    
    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        loop_manager: Optional[LoopManager] = None,
        llm_client: Optional[LLMClient] = None
    ):
        self.config = config or EngineConfig()
        self.loop_manager = loop_manager or LoopManager()
        self.llm_client = llm_client or LLMClient('antigravity')
        self.prompt_builder = PromptBuilder(self.config.completion_promise)
        self.completion_detector = CompletionDetector(self.config.completion_promise)
    
    def estimate_tokens(self, text: str) -> int:
        """Estima tokens baseado em caracteres (1 token ~ 4 chars)"""
        return len(text) // 4
    
    def estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        """Estima custo em USD"""
        cost_in = (tokens_in / 1000) * self.config.cost_per_1k_in
        cost_out = (tokens_out / 1000) * self.config.cost_per_1k_out
        return cost_in + cost_out
    
    def call_llm(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> IterationResult:
        """
        Chama a API do LLM.
        
        Returns:
            IterationResult com resposta ou erro
        """
        model = model or self.config.model
        tokens_in = self.estimate_tokens(prompt)
        
        start_time = time.time()
        
        try:
            # Usar LLMClient para chamada à API
            response = self.llm_client.complete(
                prompt=prompt,
                model=model,
                max_tokens=4000,
                temperature=0.7
            )
            
            duration = time.time() - start_time
            
            if not response.success:
                return IterationResult(
                    success=False,
                    response="",
                    tokens_in=tokens_in,
                    tokens_out=0,
                    duration_seconds=duration,
                    completed=False,
                    error=response.error
                )
            
            # Detectar completion
            completed = self.completion_detector.detect(response.content)
            
            return IterationResult(
                success=True,
                response=response.content,
                tokens_in=response.tokens_in or tokens_in,
                tokens_out=response.tokens_out,
                duration_seconds=duration,
                completed=completed
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return IterationResult(
                success=False,
                response="",
                tokens_in=tokens_in,
                tokens_out=0,
                duration_seconds=duration,
                completed=False,
                error=str(e)
            )
    
    def execute_iteration(
        self,
        loop_code: str,
        model: Optional[str] = None,
        on_progress: Optional[Callable] = None
    ) -> bool:
        """
        Executa uma única iteração de um loop.
        
        Args:
            loop_code: Código do loop
            model: Modelo a usar (opcional)
            on_progress: Callback de progresso (opcional)
            
        Returns:
            True se deve continuar, False se completou ou falhou
        """
        # Obter loop
        loop = self.loop_manager.get_loop(loop_code)
        if not loop:
            raise ValueError(f"Loop não encontrado: {loop_code}")
        
        if loop.status not in [LoopStatus.PENDING.value, LoopStatus.RUNNING.value]:
            raise ValueError(f"Loop não pode ser executado. Status: {loop.status}")
        
        # Atualizar status para running
        if loop.status == LoopStatus.PENDING.value:
            self.loop_manager.update_loop_status(loop_code, LoopStatus.RUNNING.value)
        
        # Verificar se atingiu max iterations
        if loop.current_iteration >= loop.max_iterations:
            self.loop_manager.update_loop_status(
                loop_code,
                LoopStatus.INCOMPLETE.value,
                f"Max iterations ({loop.max_iterations}) atingido sem completion"
            )
            return False
        
        # Obter iterações anteriores
        previous_iterations = self.loop_manager.get_iterations(loop_code)
        prev_summary = [
            {
                'iteration': it.iteration_number,
                'summary': it.prompt_summary,
                'result': it.response_summary
            }
            for it in previous_iterations
        ]
        
        # Construir prompt
        prompt = self.prompt_builder.build_iteration_prompt(
            task_description=loop.task_description,
            agent_slug=loop.agent_slug,
            iteration_number=loop.current_iteration + 1,
            max_iterations=loop.max_iterations,
            previous_iterations=prev_summary
        )
        
        # Chamar LLM
        result = self.call_llm(prompt, model)
        
        # Logar resultado
        iteration_num = loop.current_iteration + 1
        
        if not result.success:
            # Falha na chamada
            self.loop_manager.log_iteration(
                loop_code=loop_code,
                iteration_number=iteration_num,
                prompt_summary=prompt[:200],
                response_summary=f"ERRO: {result.error}",
                full_prompt=prompt,
                full_response=result.error,
                tokens_in=result.tokens_in,
                tokens_out=0,
                duration_seconds=int(result.duration_seconds)
            )
            self.loop_manager.increment_iteration(loop_code, result.tokens_in, 0)
            
            if on_progress:
                on_progress({
                    'iteration': iteration_num,
                    'status': 'error',
                    'error': result.error
                })
            
            return False
        
        # Sucesso - logar iteração
        response_summary = self.completion_detector.extract_summary(result.response)
        
        self.loop_manager.log_iteration(
            loop_code=loop_code,
            iteration_number=iteration_num,
            prompt_summary=prompt[:200],
            response_summary=response_summary,
            full_prompt=prompt,
            full_response=result.response,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            duration_seconds=int(result.duration_seconds)
        )
        self.loop_manager.increment_iteration(
            loop_code,
            result.tokens_in,
            result.tokens_out
        )
        
        # Verificar completion
        if result.completed or self.completion_detector.detect(result.response):
            self.loop_manager.update_loop_status(
                loop_code,
                LoopStatus.COMPLETED.value,
                response_summary
            )
            
            if on_progress:
                on_progress({
                    'iteration': iteration_num,
                    'status': 'completed',
                    'summary': response_summary
                })
            
            return False
        
        # Continuar
        if on_progress:
            on_progress({
                'iteration': iteration_num,
                'status': 'running',
                'summary': response_summary
            })
        
        return True
    
    def run_loop(
        self,
        loop_code: str,
        model: Optional[str] = None,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ):
        """
        Executa um loop completo (todas as iterações).
        
        Args:
            loop_code: Código do loop
            model: Modelo a usar
            on_progress: Callback a cada iteração
            on_complete: Callback ao completar
            on_error: Callback em caso de erro
        """
        try:
            loop = self.loop_manager.get_loop(loop_code)
            if not loop:
                raise ValueError(f"Loop não encontrado: {loop_code}")
            
            print(f"🚀 Iniciando loop {loop_code}")
            print(f"   Agente: {loop.agent_slug}")
            print(f"   Max iterations: {loop.max_iterations}")
            
            # Executar iterações
            should_continue = True
            while should_continue:
                should_continue = self.execute_iteration(
                    loop_code=loop_code,
                    model=model,
                    on_progress=on_progress
                )
            
            # Verificar status final
            loop = self.loop_manager.get_loop(loop_code)
            
            if on_complete:
                on_complete({
                    'loop_code': loop_code,
                    'status': loop.status,
                    'iterations': loop.current_iteration,
                    'summary': loop.result_summary
                })
            
            print(f"✅ Loop {loop_code} finalizado: {loop.status}")
            
        except Exception as e:
            print(f"❌ Erro no loop {loop_code}: {e}")
            
            # Marcar como falha
            try:
                self.loop_manager.update_loop_status(
                    loop_code,
                    LoopStatus.FAILED.value,
                    str(e)
                )
            except:
                pass
            
            if on_error:
                on_error({'loop_code': loop_code, 'error': str(e)})
    
    def get_loop_report(self, loop_code: str) -> Dict:
        """
        Gera um relatório completo de um loop.
        
        Returns:
            Dict com métricas e histórico
        """
        loop = self.loop_manager.get_loop(loop_code)
        if not loop:
            return {'error': 'Loop não encontrado'}
        
        iterations = self.loop_manager.get_iterations(loop_code)
        
        total_duration = sum(it.duration_seconds for it in iterations)
        avg_duration = total_duration / len(iterations) if iterations else 0
        
        estimated_cost = self.estimate_cost(
            loop.total_tokens_in,
            loop.total_tokens_out
        )
        
        return {
            'loop_code': loop_code,
            'agent': loop.agent_slug,
            'status': loop.status,
            'task': loop.task_description,
            'iterations': {
                'completed': loop.current_iteration,
                'max': loop.max_iterations,
                'list': [it.to_dict() for it in iterations]
            },
            'tokens': {
                'in': loop.total_tokens_in,
                'out': loop.total_tokens_out,
                'total': loop.total_tokens_in + loop.total_tokens_out
            },
            'cost': {
                'estimated_usd': round(estimated_cost, 4)
            },
            'timing': {
                'total_seconds': total_duration,
                'avg_per_iteration': round(avg_duration, 2)
            },
            'result': loop.result_summary
        }


# CLI para testes
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Ralph Iteration Engine')
    parser.add_argument('command', choices=['run', 'report', 'test'])
    parser.add_argument('--loop-code', help='Código do loop')
    parser.add_argument('--model', default='kimi-coding/k2p5', help='Modelo a usar')
    
    args = parser.parse_args()
    
    engine = IterationEngine()
    
    if args.command == 'report':
        if not args.loop_code:
            print("❌ --loop-code obrigatório")
            sys.exit(1)
        
        report = engine.get_loop_report(args.loop_code)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif args.command == 'test':
        print("🧪 Testando IterationEngine...")
        
        # Testar prompt builder
        builder = PromptBuilder()
        prompt = builder.build_first_iteration_prompt(
            task_description="Criar API REST",
            agent_slug="dev",
            max_iterations=10
        )
        assert "Iteração 1 de 10" in prompt
        print("✅ PromptBuilder funciona")
        
        # Testar completion detector
        detector = CompletionDetector()
        assert detector.detect("Texto RALPH_COMPLETE aqui") == True
        assert detector.detect("Texto normal") == False
        print("✅ CompletionDetector funciona")
        
        # Testar estimativa de tokens
        tokens = engine.estimate_tokens("A" * 400)  # 400 chars
        assert tokens == 100  # 400 / 4
        print("✅ Estimativa de tokens funciona")
        
        # Testar estimativa de custo
        cost = engine.estimate_cost(2000, 1000)
        expected = (2 * 0.001) + (1 * 0.003)  # $0.005
        assert abs(cost - expected) < 0.0001
        print("✅ Estimativa de custo funciona")
        
        print("\n🎉 Todos os testes passaram!")
        print("⚠️  Nota: A chamada à API LLM ainda não está implementada.")
        print("   Integrar com Antigravity na Fase 3.")
    
    else:
        print(f"Comando: {args.command}")
        print("Use 'test' para testar ou 'report --loop-code XXX' para relatório")
