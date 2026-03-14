#!/usr/bin/env python3
"""
Deployer Agent - Especialista em deploy via comandos naturais
"""

import os
import re
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from project_registry import get_registry, ProjectConfig
from live_logger import get_logger

@dataclass
class DeployResult:
    success: bool
    message: str
    url: Optional[str] = None
    duration: float = 0.0
    error: Optional[str] = None
    logs: List[str] = None

class DeployerAgent:
    """Agent especializado em deploy com feedback em tempo real"""
    
    PLATFORMS = {
        'vercel': {
            'detect': lambda p: (p / 'vercel.json').exists() or 'vercel' in _read_package_json(p, ''),
            'deploy_cmd': 'npx vercel --prod --yes',
            'env_vars': ['VERCEL_TOKEN', 'VERCEL_ORG_ID', 'VERCEL_PROJECT_ID'],
            'url_pattern': r'(https?://[^\s]+\.vercel\.app)'
        },
        'railway': {
            'detect': lambda p: (p / 'railway.json').exists() or (p / 'railway.yml').exists(),
            'deploy_cmd': 'railway up --detach',
            'env_vars': ['RAILWAY_TOKEN'],
            'url_pattern': r'(https?://[^\s]+\.up\.railway\.app)'
        },
        'docker': {
            'detect': lambda p: (p / 'Dockerfile').exists(),
            'deploy_cmd': 'docker build -t {name} . && docker push {name}',
            'env_vars': ['DOCKER_REGISTRY', 'DOCKER_USERNAME'],
            'url_pattern': None
        },
        'github_pages': {
            'detect': lambda p: (p / '.github' / 'workflows').exists(),
            'deploy_cmd': 'npm run build && npx gh-pages -d {output_dir}',
            'env_vars': ['GITHUB_TOKEN'],
            'url_pattern': r'(https?://[^\s]+\.github\.io/[^\s]+)'
        },
        'netlify': {
            'detect': lambda p: (p / 'netlify.toml').exists(),
            'deploy_cmd': 'npx netlify deploy --prod --dir={output_dir}',
            'env_vars': ['NETLIFY_AUTH_TOKEN', 'NETLIFY_SITE_ID'],
            'url_pattern': r'(https?://[^\s]+\.netlify\.app)'
        }
    }
    
    def __init__(self):
        self.registry = get_registry()
        self.logger = get_logger()
        self.current_mission: Optional[str] = None
    
    async def handle_command(self, command: str, mission_id: str = None) -> DeployResult:
        """
        Processa comando natural de deploy.
        
        Exemplos:
        - "deploya o meu-app"
        - "deploya o dashboard pra produção"
        - "deploya o api na railway"
        - "faz deploy do frontend com Node 20"
        """
        self.current_mission = mission_id or f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Parse o comando
        project_name, platform, env, adjustments = self._parse_command(command)
        
        await self.logger.step("deployer", "parse_command", "completed", {
            "project": project_name,
            "platform": platform,
            "env": env,
            "adjustments": adjustments
        }, self.current_mission)
        
        # Busca projeto
        project = self.registry.get_project(project_name)
        if not project:
            return DeployResult(
                success=False,
                message=f"❌ Projeto '{project_name}' não encontrado.",
                error="PROJECT_NOT_FOUND"
            )
        
        await self.logger.info("deployer", f"Projeto encontrado: {project.name} em {project.path}",
                               mission_id=self.current_mission)
        
        # Se não achou plataforma no comando, usa a do projeto
        if not platform:
            platform = project.platform
        
        # Aplica ajustes (ex: "usa Node 20")
        if adjustments:
            project = self._apply_adjustments(project, adjustments)
        
        # Executa deploy
        return await self._deploy(project, platform, env)
    
    def _parse_command(self, command: str) -> Tuple[str, Optional[str], str, List[str]]:
        """
        Extrai info do comando natural.
        Retorna: (project_name, platform, env, adjustments)
        """
        command_lower = command.lower()
        
        # Detecta plataforma
        platform = None
        for plat in self.PLATFORMS.keys():
            if plat in command_lower or plat.replace('_', '') in command_lower:
                platform = plat
                break
        
        # Detecta ambiente
        env = 'production'
        if any(word in command_lower for word in ['staging', 'homolog', 'hml']):
            env = 'staging'
        if any(word in command_lower for word in ['dev', 'development', 'local']):
            env = 'development'
        
        # Detecta ajustes
        adjustments = []
        adjustment_patterns = [
            r'usa(?:r)?\s+(?:node|nodejs?)\s+(\d+)',
            r'com\s+(?:node|nodejs?)\s+(\d+)',
            r'build\s+com\s+(\w+)',
        ]
        for pattern in adjustment_patterns:
            match = re.search(pattern, command_lower)
            if match:
                adjustments.append(match.group(0))
        
        # Extrai nome do projeto
        # Remove palavras comuns e pega o que sobra
        words = command_lower.replace(',', ' ').replace('.', ' ').split()
        ignore_words = {'deploya', 'deploy', 'faz', 'o', 'a', 'os', 'as', 'do', 'da', 
                       'pra', 'para', 'pro', 'na', 'no', 'em', 'com', 'usar', 'usa',
                       'produção', 'prod', 'staging', 'dev', 'node', 'nodejs'}
        
        # Tenta achar nome entre aspas primeiro
        quoted = re.findall(r'["\']([^"\']+)["\']', command)
        if quoted:
            project_name = quoted[0]
        else:
            # Pega a primeira palavra que não está na ignore list
            project_name = None
            for word in words:
                clean_word = re.sub(r'[^\w-]', '', word)
                if clean_word and clean_word not in ignore_words:
                    project_name = clean_word
                    break
        
        if not project_name:
            project_name = words[-1] if words else "unknown"
        
        return project_name, platform, env, adjustments
    
    def _apply_adjustments(self, project: ProjectConfig, adjustments: List[str]) -> ProjectConfig:
        """Aplica ajustes ao projeto"""
        # Por enquanto só loga, depois pode modificar o config
        for adj in adjustments:
            if 'node' in adj.lower():
                # Extrai versão do Node
                match = re.search(r'(\d+)', adj)
                if match:
                    version = match.group(1)
                    # Aqui poderia atualizar o .nvmrc ou package.json engines
                    pass
        return project
    
    async def _deploy(self, project: ProjectConfig, platform: str, env: str) -> DeployResult:
        """Executa o deploy propriamente dito"""
        start_time = datetime.now()
        
        await self.logger.step("deployer", "validate", "started", 
                               {"platform": platform}, self.current_mission)
        
        # Valida pré-requisitos
        valid, error = self._validate_project(project, platform)
        if not valid:
            await self.logger.step("deployer", "validate", "failed", 
                                   {"error": error}, self.current_mission)
            return DeployResult(success=False, message=f"❌ {error}", error=error)
        
        await self.logger.step("deployer", "validate", "completed", mission_id=self.current_mission)
        
        # Build
        await self.logger.step("deployer", "build", "started", mission_id=self.current_mission)
        build_result = await self._run_build(project)
        if not build_result.success:
            await self.logger.step("deployer", "build", "failed", 
                                   {"error": build_result.error}, self.current_mission)
            return build_result
        await self.logger.step("deployer", "build", "completed", 
                               {"duration": build_result.duration}, self.current_mission)
        
        # Deploy
        await self.logger.step("deployer", "deploy", "started", 
                               {"platform": platform}, self.current_mission)
        deploy_result = await self._run_platform_deploy(project, platform)
        if not deploy_result.success:
            await self.logger.step("deployer", "deploy", "failed", 
                                   {"error": deploy_result.error}, self.current_mission)
            return deploy_result
        await self.logger.step("deployer", "deploy", "completed", 
                               {"url": deploy_result.url}, self.current_mission)
        
        # Health check
        if project.health_check_url:
            await self.logger.step("deployer", "health_check", "started", 
                                   {"url": project.health_check_url}, self.current_mission)
            health_ok = await self._health_check(project.health_check_url, project.health_check_timeout)
            if not health_ok:
                await self.logger.step("deployer", "health_check", "failed", 
                                       {"url": project.health_check_url}, self.current_mission)
                # Rollback se configurado
                await self._rollback(platform)
                return DeployResult(
                    success=False,
                    message="❌ Health check falhou. Deploy revertido.",
                    url=deploy_result.url,
                    error="HEALTH_CHECK_FAILED"
                )
            await self.logger.step("deployer", "health_check", "completed", 
                                   {"status": "200 OK"}, self.current_mission)
        
        # Marca como deployado
        self._mark_deployed(project.path)
        
        duration = (datetime.now() - start_time).total_seconds()
        await self.logger.success("deployer", f"✅ Deploy completo em {duration:.1f}s", 
                                  {"url": deploy_result.url}, self.current_mission)
        
        return DeployResult(
            success=True,
            message=f"✅ Deploy completo!",
            url=deploy_result.url,
            duration=duration
        )
    
    def _validate_project(self, project: ProjectConfig, platform: str) -> Tuple[bool, Optional[str]]:
        """Valida se projeto pode ser deployado"""
        if not project.path.exists():
            return False, f"Diretório não existe: {project.path}"
        
        # Verifica env vars necessárias
        if platform in self.PLATFORMS:
            required_vars = self.PLATFORMS[platform].get('env_vars', [])
            missing = [v for v in required_vars if not os.getenv(v)]
            if missing:
                return False, f"Variáveis de ambiente faltando: {', '.join(missing)}"
        
        return True, None
    
    async def _run_build(self, project: ProjectConfig) -> DeployResult:
        """Executa build do projeto"""
        start = datetime.now()
        
        try:
            proc = await asyncio.create_subprocess_shell(
                f"cd {project.path} && {project.build_cmd}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            duration = (datetime.now() - start).total_seconds()
            
            if proc.returncode != 0:
                error = stderr.decode()[-500:] if stderr else "Build failed"
                return DeployResult(
                    success=False,
                    message="❌ Build falhou",
                    error=error,
                    duration=duration
                )
            
            return DeployResult(
                success=True,
                message="✅ Build completo",
                duration=duration
            )
            
        except Exception as e:
            return DeployResult(
                success=False,
                message="❌ Erro no build",
                error=str(e)
            )
    
    async def _run_platform_deploy(self, project: ProjectConfig, platform: str) -> DeployResult:
        """Executa deploy na plataforma específica"""
        if platform not in self.PLATFORMS:
            return DeployResult(
                success=False,
                message=f"❌ Plataforma '{platform}' não suportada",
                error="UNSUPPORTED_PLATFORM"
            )
        
        plat_config = self.PLATFORMS[platform]
        cmd = plat_config['deploy_cmd'].format(
            name=project.name,
            output_dir=project.output_dir
        )
        
        try:
            proc = await asyncio.create_subprocess_shell(
                f"cd {project.path} && {cmd}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            output = (stdout or b'').decode() + (stderr or b'').decode()
            
            if proc.returncode != 0:
                return DeployResult(
                    success=False,
                    message=f"❌ Deploy na {platform} falhou",
                    error=output[-1000:]
                )
            
            # Extrai URL do output
            url = None
            if plat_config['url_pattern']:
                match = re.search(plat_config['url_pattern'], output)
                if match:
                    url = match.group(1)
            
            return DeployResult(
                success=True,
                message=f"✅ Deploy na {platform} completo",
                url=url
            )
            
        except Exception as e:
            return DeployResult(
                success=False,
                message="❌ Erro no deploy",
                error=str(e)
            )
    
    async def _health_check(self, url: str, timeout: int) -> bool:
        """Faz health check na URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def _rollback(self, platform: str):
        """Tenta fazer rollback (se suportado pela plataforma)"""
        # Implementação específica por plataforma
        pass
    
    def _mark_deployed(self, path: Path):
        """Marca projeto como deployado"""
        marker = path / '.ralph-deployed'
        marker.write_text(datetime.now().isoformat())
    
    def list_available_projects(self) -> str:
        """Retorna lista formatada de projetos"""
        projects = self.registry.list_projects()
        if not projects:
            return "Nenhum projeto configurado. Crie um .ralph-deploy.yml nos seus projetos."
        
        lines = ["📁 Projetos disponíveis para deploy:"]
        for p in projects:
            status = "🟢" if not p['modified'] and p['ahead'] == 0 else "🟡"
            branch_info = f"[{p['branch']}]" if p['branch'] else "[no git]"
            ahead_info = f" ↑{p['ahead']}" if p['ahead'] > 0 else ""
            lines.append(f"  {status} {p['name']} {branch_info}{ahead_info} ({p['type']} → {p['platform']})")
        
        return "\n".join(lines)


def _read_package_json(path: Path, default: str) -> str:
    """Lê package.json se existir"""
    try:
        import json
        with open(path / 'package.json') as f:
            data = json.load(f)
        return json.dumps(data)
    except:
        return default


# Singleton
deployer = DeployerAgent()

if __name__ == "__main__":
    async def test():
        d = DeployerAgent()
        print(d.list_available_projects())
    
    asyncio.run(test())
