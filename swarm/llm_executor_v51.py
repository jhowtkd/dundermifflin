#!/usr/bin/env python3
"""
Ralph Swarm - LLM Executor v5.1
Chamada direta à API em vez de CLI
"""

import os
import sys
import json
import time
import requests
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import threading

# Configurações de modelos
MODEL_CONFIGS = {
    'kimi-k2': {
        'provider': 'kimi-code',
        'api_url': 'https://api.kimi.com/coding/v1/chat/completions',
        'model': 'kimi-for-coding',
        'cost_per_1k_input': 0.002,
        'cost_per_1k_output': 0.008,
        'max_tokens': 32000,
        'timeout': 180
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

def get_api_key():
    """Obtém API key do arquivo de config OAuth"""
    oauth_file = Path.home() / ".kimi/oauth/oauth/kimi-code"
    if oauth_file.exists():
        try:
            with open(oauth_file) as f:
                data = json.load(f)
                return data.get('access_token', '')
        except:
            pass
    
    # Fallback: tenta pegar do env
    return os.getenv('KIMI_API_KEY', '')

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

class LLMExecutor:
    """Executor de LLMs com chamada direta à API"""
    
    def __init__(self, max_parallel: int = 5):
        self.rate_limiter = RateLimiter(max_parallel=max_parallel)
        self.running_calls: Dict[str, LLMCall] = {}
        self.api_key = get_api_key()
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima tokens aproximados"""
        return len(text) // 4
    
    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calcula custo da chamada"""
        config = MODEL_CONFIGS.get(model, MODEL_CONFIGS['kimi-k2'])
        
        input_cost = (tokens_in / 1000) * config['cost_per_1k_input']
        output_cost = (tokens_out / 1000) * config['cost_per_1k_output']
        
        return input_cost + output_cost
    
    def _call_llm_api(self, call: LLMCall) -> LLMCall:
        """
        Faz chamada direta à API HTTP.
        """
        model_config = MODEL_CONFIGS.get(call.model, MODEL_CONFIGS['kimi-k2'])
        
        start_time = time.time()
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model': model_config['model'],
                'messages': [
                    {'role': 'user', 'content': call.prompt}
                ],
                'max_tokens': model_config['max_tokens']
            }
            
            response = requests.post(
                model_config['api_url'],
                headers=headers,
                json=payload,
                timeout=model_config['timeout']
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code != 200:
                call.error = f"API error {response.status_code}: {response.text}"
                call.duration_ms = duration_ms
                return call
            
            data = response.json()
            
            # Extrair resposta
            if 'choices' in data and len(data['choices']) > 0:
                call.response = data['choices'][0]['message']['content']
            else:
                call.error = "No response in API output"
                call.duration_ms = duration_ms
                return call
            
            # Calcular tokens
            call.tokens_in = data.get('usage', {}).get('prompt_tokens', self._estimate_tokens(call.prompt))
            call.tokens_out = data.get('usage', {}).get('completion_tokens', self._estimate_tokens(call.response))
            call.duration_ms = duration_ms
            call.cost_usd = self._calculate_cost(call.model, call.tokens_in, call.tokens_out)
            
        except requests.Timeout:
            call.error = f"Timeout after {model_config['timeout']}s"
            call.duration_ms = int((time.time() - start_time) * 1000)
        except Exception as e:
            call.error = str(e)
            call.duration_ms = int((time.time() - start_time) * 1000)
        
        return call
    
    def execute_single(self, agent_slug: str, prompt: str, model: Optional[str] = None) -> LLMCall:
        """Executa uma única chamada de LLM"""
        if model is None:
            model = AGENT_MODELS.get(agent_slug, 'kimi-k2')
        
        call = LLMCall(
            agent_slug=agent_slug,
            prompt=prompt,
            model=model
        )
        
        self.rate_limiter.acquire()
        
        try:
            call = self._call_llm_api(call)
        finally:
            self.rate_limiter.release()
        
        return call
    
    def execute_parallel(self, calls_config: List[Dict]) -> List[LLMCall]:
        """Executa múltiplas chamadas em paralelo"""
        results = []
        
        def execute_one(config):
            return self.execute_single(
                config['agent_slug'],
                config['prompt'],
                config.get('model')
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_call = {
                executor.submit(execute_one, config): config 
                for config in calls_config
            }
            
            for future in concurrent.futures.as_completed(future_to_call):
                try:
                    call = future.result()
                    results.append(call)
                except Exception as e:
                    config = future_to_call[future]
                    call = LLMCall(
                        agent_slug=config['agent_slug'],
                        prompt=config['prompt'],
                        model=config.get('model', 'kimi-k2'),
                        error=str(e)
                    )
                    results.append(call)
        
        return results

# Singleton
_llm_executor = None

def get_executor(max_parallel: int = 5) -> LLMExecutor:
    """Retorna singleton do executor"""
    global _llm_executor
    if _llm_executor is None:
        _llm_executor = LLMExecutor(max_parallel=max_parallel)
    return _llm_executor


if __name__ == "__main__":
    # Teste
    executor = LLMExecutor()
    result = executor.execute_single("test", "Qual é a capital do Brasil?")
    print(f"Response: {result.response}")
    print(f"Error: {result.error}")
    print(f"Cost: ${result.cost_usd:.4f}")
