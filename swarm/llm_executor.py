#!/usr/bin/env python3
"""
Ralph Swarm - LLM Executor v5.0
Executor real de LLMs com paralelismo, rate limiting e tracking de custo
"""

import os
import sys
import json
import time
import subprocess
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading

# Model configurations
MODEL_CONFIGS = {
    'gemini-flash': {
        'provider': 'google-antigravity',
        'model': 'gemini-3-flash',
        'cost_per_1k_input': 0.0001,   # $0.10 per 1M tokens
        'cost_per_1k_output': 0.0004,  # $0.40 per 1M tokens
        'max_tokens': 8192,
        'timeout': 60
    },
    'gemini-pro': {
        'provider': 'google-antigravity',
        'model': 'gemini-3-pro',
        'cost_per_1k_input': 0.0035,   # $3.50 per 1M tokens
        'cost_per_1k_output': 0.0105,  # $10.50 per 1M tokens
        'max_tokens': 8192,
        'timeout': 120
    },
    'kimi-k2': {
        'provider': 'kimi-code',
        'model': 'kimi-for-coding',
        'cost_per_1k_input': 0.002,    # Estimado
        'cost_per_1k_output': 0.008,   # Estimado
        'max_tokens': 32000,
        'timeout': 180
    },
    'claude-haiku': {
        'provider': 'anthropic',
        'model': 'claude-3-haiku',
        'cost_per_1k_input': 0.00025,
        'cost_per_1k_output': 0.00125,
        'max_tokens': 4096,
        'timeout': 60
    },
    'claude-sonnet': {
        'provider': 'anthropic',
        'model': 'claude-3-sonnet',
        'cost_per_1k_input': 0.003,
        'cost_per_1k_output': 0.015,
        'max_tokens': 4096,
        'timeout': 120
    }
}

# Agent to model mapping
AGENT_MODELS = {
    'ralph': 'kimi-k2',
    'scout': 'kimi-k2',
    'max': 'kimi-k2',
    'maya': 'kimi-k2',
    'tracker': 'kimi-k2',
    'watcher': 'kimi-k2'
}

@dataclass
class LLMCall:
    """Representa uma chamada de LLM"""
    agent_slug: str
    prompt: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Result
    response: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'agent': self.agent_slug,
            'model': self.model,
            'timestamp': self.timestamp.isoformat(),
            'tokens_in': self.tokens_in,
            'tokens_out': self.tokens_out,
            'cost_usd': self.cost_usd,
            'duration_ms': self.duration_ms,
            'success': self.error is None,
            'error': self.error
        }

class RateLimiter:
    """Rate limiter para controle de chamadas paralelas"""
    
    def __init__(self, max_parallel: int = 5, min_delay_ms: int = 100):
        self.max_parallel = max_parallel
        self.min_delay_ms = min_delay_ms
        self.semaphore = threading.Semaphore(max_parallel)
        self.last_call_time = 0
        self.lock = threading.Lock()
    
    def acquire(self):
        """Adquire permissão para fazer chamada"""
        self.semaphore.acquire()
        
        # Rate limiting por tempo
        with self.lock:
            current_time = time.time() * 1000
            time_since_last = current_time - self.last_call_time
            
            if time_since_last < self.min_delay_ms:
                sleep_time = (self.min_delay_ms - time_since_last) / 1000
                time.sleep(sleep_time)
            
            self.last_call_time = time.time() * 1000
    
    def release(self):
        """Libera permissão"""
        self.semaphore.release()

class CostTracker:
    """Tracking de custos de LLM"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.calls: List[LLMCall] = []
        self.lock = threading.Lock()
        self.log_file = log_file or Path.home() / ".openclaw/workspace/projects/dunder-mifflin/swarm/cost_log.jsonl"
    
    def add_call(self, call: LLMCall):
        """Adiciona chamada ao tracking"""
        with self.lock:
            self.calls.append(call)
            
            # Salvar em arquivo
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(call.to_dict()) + '\n')
    
    def get_total_cost(self) -> float:
        """Retorna custo total acumulado"""
        return sum(c.cost_usd for c in self.calls)
    
    def get_cost_by_agent(self) -> Dict[str, float]:
        """Retorna custo por agent"""
        costs = {}
        for call in self.calls:
            costs[call.agent_slug] = costs.get(call.agent_slug, 0) + call.cost_usd
        return costs
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de uso"""
        if not self.calls:
            return {
                'total_calls': 0,
                'total_cost': 0,
                'avg_cost_per_call': 0,
                'total_tokens': 0
            }
        
        total_tokens = sum(c.tokens_in + c.tokens_out for c in self.calls)
        successful = sum(1 for c in self.calls if c.error is None)
        
        return {
            'total_calls': len(self.calls),
            'successful_calls': successful,
            'failed_calls': len(self.calls) - successful,
            'total_cost': self.get_total_cost(),
            'avg_cost_per_call': self.get_total_cost() / len(self.calls),
            'total_tokens': total_tokens,
            'cost_by_agent': self.get_cost_by_agent()
        }

class LLMExecutor:
    """
    Executor de LLMs com paralelismo, rate limiting e tracking.
    """
    
    def __init__(self, max_parallel: int = 5):
        self.rate_limiter = RateLimiter(max_parallel=max_parallel)
        self.cost_tracker = CostTracker()
        self.running_calls: Dict[str, LLMCall] = {}
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima tokens aproximados (regra simples: ~4 chars por token)"""
        return len(text) // 4
    
    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calcula custo da chamada"""
        config = MODEL_CONFIGS.get(model, MODEL_CONFIGS['gemini-flash'])
        
        input_cost = (tokens_in / 1000) * config['cost_per_1k_input']
        output_cost = (tokens_out / 1000) * config['cost_per_1k_output']
        
        return input_cost + output_cost
    
    def _call_llm(self, call: LLMCall) -> LLMCall:
        """
        Faz chamada real ao LLM via kimi CLI usando stdin.
        """
        model_config = MODEL_CONFIGS.get(call.model, MODEL_CONFIGS['kimi-k2'])
        provider_model = f"{model_config['provider']}/{model_config['model']}"
        
        start_time = time.time()
        
        try:
            # Usar stdin em vez de --prompt
            process = subprocess.Popen(
                ['kimi', '--model', provider_model, '--print', '--quiet'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=call.prompt,
                timeout=model_config['timeout']
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if process.returncode != 0:
                call.error = f"kimi CLI error: {stderr}"
                call.duration_ms = duration_ms
                return call
            
            # Sucesso
            call.response = stdout
            call.tokens_in = self._estimate_tokens(call.prompt)
            call.tokens_out = self._estimate_tokens(call.response)
            call.duration_ms = duration_ms
            call.cost_usd = self._calculate_cost(call.model, call.tokens_in, call.tokens_out)
            
        except subprocess.TimeoutExpired:
            call.error = f"Timeout after {model_config['timeout']}s"
            call.duration_ms = int((time.time() - start_time) * 1000)
        except Exception as e:
            call.error = str(e)
            call.duration_ms = int((time.time() - start_time) * 1000)
        
        return call
    
    def execute_single(self, agent_slug: str, prompt: str, model: Optional[str] = None) -> LLMCall:
        """
        Executa uma única chamada de LLM.
        
        Args:
            agent_slug: ID do agent
            prompt: Prompt completo
            model: Modelo específico (ou None para usar default do agent)
            
        Returns:
            LLMCall com resultado e métricas
        """
        # Determinar modelo
        if model is None:
            model = AGENT_MODELS.get(agent_slug, 'gemini-flash')
        
        # Criar call
        call = LLMCall(
            agent_slug=agent_slug,
            prompt=prompt,
            model=model
        )
        
        # Rate limiting
        self.rate_limiter.acquire()
        
        try:
            # Executar
            call = self._call_llm(call)
        finally:
            self.rate_limiter.release()
        
        # Tracking
        self.cost_tracker.add_call(call)
        
        return call
    
    def execute_parallel(self, calls_config: List[Dict]) -> List[LLMCall]:
        """
        Executa múltiplas chamadas em paralelo.
        
        Args:
            calls_config: Lista de dicts com 'agent_slug', 'prompt', opcional 'model'
            
        Returns:
            Lista de LLMCall com resultados
        """
        results = []
        
        def execute_one(config: Dict) -> LLMCall:
            return self.execute_single(
                agent_slug=config['agent_slug'],
                prompt=config['prompt'],
                model=config.get('model')
            )
        
        # Executar em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_config = {
                executor.submit(execute_one, config): config 
                for config in calls_config
            }
            
            for future in concurrent.futures.as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    call = future.result()
                    results.append(call)
                except Exception as e:
                    # Criar call de erro
                    error_call = LLMCall(
                        agent_slug=config['agent_slug'],
                        prompt=config['prompt'],
                        model=config.get('model', 'gemini-flash'),
                        error=str(e)
                    )
                    results.append(error_call)
        
        return results
    
    def get_cost_summary(self) -> Dict:
        """Retorna resumo de custos"""
        return self.cost_tracker.get_stats()


# Teste
if __name__ == '__main__':
    print("🚀 LLM Executor - Teste")
    print("=" * 60)
    
    executor = LLMExecutor(max_parallel=2)
    
    # Teste 1: Chamada única
    print("\n1️⃣ Testando chamada única (Scout):")
    call = executor.execute_single(
        agent_slug='scout',
        prompt="Liste 3 ferramentas de produtividade populares. Responda em português."
    )
    
    if call.error:
        print(f"   ❌ Erro: {call.error}")
    else:
        print(f"   ✅ Sucesso!")
        print(f"   📝 Resposta: {call.response[:100]}...")
        print(f"   💰 Custo: ${call.cost_usd:.6f}")
        print(f"   🔢 Tokens: {call.tokens_in} in, {call.tokens_out} out")
        print(f"   ⏱️  Duração: {call.duration_ms}ms")
    
    # Teste 2: Chamadas paralelas
    print("\n2️⃣ Testando chamadas paralelas:")
    calls = [
        {
            'agent_slug': 'scout',
            'prompt': 'Liste 2 concorrentes de Notion.'
        },
        {
            'agent_slug': 'maya',
            'prompt': 'Crie 2 headlines para ferramenta de produtividade.'
        }
    ]
    
    start = time.time()
    results = executor.execute_parallel(calls)
    duration = time.time() - start
    
    print(f"   ✅ {len(results)} chamadas completadas em {duration:.2f}s")
    for r in results:
        status = "✅" if not r.error else "❌"
        print(f"   {status} {r.agent_slug}: ${r.cost_usd:.6f} - {r.duration_ms}ms")
    
    # Resumo de custos
    print("\n3️⃣ Resumo de custos:")
    stats = executor.get_cost_summary()
    print(f"   💰 Total: ${stats['total_cost']:.6f}")
    print(f"   📊 Chamadas: {stats['total_calls']}")
    print(f"   💵 Média por chamada: ${stats['avg_cost_per_call']:.6f}")
    
    print("\n" + "=" * 60)
    print("✅ Testes completados!")
