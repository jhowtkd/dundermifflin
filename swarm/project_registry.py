#!/usr/bin/env python3
"""
Project Registry - Descobre e gerencia projetos com .ralph-deploy.yml
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import subprocess

@dataclass
class ProjectConfig:
    name: str
    path: Path
    type: str
    platform: str
    build_cmd: str
    output_dir: str
    env_file: Optional[str]
    health_check_url: Optional[str]
    health_check_timeout: int
    notify_on: List[str]
    auto_deploy_branch: Optional[str]
    auto_deploy_on_push: bool

class ProjectRegistry:
    """Registro de projetos detectados automaticamente"""
    
    DISCOVERY_PATHS = [
        Path.home() / "projetos",
        Path.home() / "workspace", 
        Path.home() / "dev",
        Path.home() / ".openclaw" / "workspace" / "projects",
        Path.home() / ".openclaw" / "workspace",
    ]
    
    def __init__(self):
        self.projects: Dict[str, ProjectConfig] = {}
        self._scan_projects()
    
    def _scan_projects(self):
        """Scaneia todos os paths procurando .ralph-deploy.yml"""
        for base_path in self.DISCOVERY_PATHS:
            if not base_path.exists():
                continue
            
            for deploy_file in base_path.rglob(".ralph-deploy.yml"):
                try:
                    config = self._parse_config(deploy_file)
                    if config:
                        self.projects[config.name] = config
                except Exception as e:
                    print(f"⚠️ Erro parseando {deploy_file}: {e}")
    
    def _parse_config(self, deploy_file: Path) -> Optional[ProjectConfig]:
        """Parseia arquivo .ralph-deploy.yml"""
        with open(deploy_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data or 'project' not in data:
            return None
        
        project = data['project']
        deploy = data.get('deploy', {})
        health = deploy.get('health_check', {})
        notify = deploy.get('notify', {})
        auto = deploy.get('auto_deploy', {})
        
        return ProjectConfig(
            name=project.get('name', deploy_file.parent.name),
            path=deploy_file.parent,
            type=project.get('type', 'unknown'),
            platform=deploy.get('platform', 'vercel'),
            build_cmd=deploy.get('build_cmd', 'npm run build'),
            output_dir=deploy.get('output_dir', 'dist'),
            env_file=deploy.get('env_file'),
            health_check_url=health.get('url'),
            health_check_timeout=health.get('timeout', 30),
            notify_on=notify.get('on', ['success', 'failure']),
            auto_deploy_branch=auto.get('branch'),
            auto_deploy_on_push=auto.get('on_push', False)
        )
    
    def get_project(self, name: str) -> Optional[ProjectConfig]:
        """Busca projeto por nome"""
        # Tenta match exato primeiro
        if name in self.projects:
            return self.projects[name]
        
        # Tenta match parcial (case insensitive)
        name_lower = name.lower()
        for proj_name, config in self.projects.items():
            if name_lower in proj_name.lower():
                return config
        
        return None
    
    def list_projects(self) -> List[Dict]:
        """Lista todos os projetos com status git"""
        result = []
        for config in self.projects.values():
            git_info = self._get_git_info(config.path)
            result.append({
                'name': config.name,
                'path': str(config.path),
                'type': config.type,
                'platform': config.platform,
                'branch': git_info.get('branch'),
                'ahead': git_info.get('ahead', 0),
                'modified': git_info.get('modified', False),
                'last_deploy': self._get_last_deploy(config.path)
            })
        return result
    
    def _get_git_info(self, path: Path) -> Dict:
        """Pega info do git do projeto"""
        try:
            # Branch atual
            branch = subprocess.run(
                ['git', '-C', str(path), 'branch', '--show-current'],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            
            # Commits ahead
            ahead_result = subprocess.run(
                ['git', '-C', str(path), 'rev-list', '--count', f'origin/{branch}..HEAD'],
                capture_output=True, text=True, timeout=5
            )
            ahead = int(ahead_result.stdout.strip()) if ahead_result.returncode == 0 else 0
            
            # Arquivos modificados
            status = subprocess.run(
                ['git', '-C', str(path), 'status', '--porcelain'],
                capture_output=True, text=True, timeout=5
            )
            modified = len(status.stdout.strip()) > 0
            
            return {'branch': branch, 'ahead': ahead, 'modified': modified}
        except:
            return {'branch': None, 'ahead': 0, 'modified': False}
    
    def _get_last_deploy(self, path: Path) -> Optional[str]:
        """Pega timestamp do último deploy"""
        marker = path / '.ralph-deployed'
        if marker.exists():
            return marker.read_text().strip()
        return None
    
    def create_config(self, path: Path, name: str, proj_type: str = 'nextjs', 
                      platform: str = 'vercel') -> ProjectConfig:
        """Cria configuração para novo projeto"""
        config_path = path / '.ralph-deploy.yml'
        
        config = {
            'project': {
                'name': name,
                'type': proj_type
            },
            'deploy': {
                'platform': platform,
                'build_cmd': self._detect_build_cmd(path, proj_type),
                'output_dir': self._detect_output_dir(proj_type),
                'health_check': {
                    'url': None,
                    'timeout': 30
                },
                'notify': {
                    'on': ['success', 'failure']
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        return self._parse_config(config_path)
    
    def _detect_build_cmd(self, path: Path, proj_type: str) -> str:
        """Detecta comando de build baseado no tipo"""
        commands = {
            'nextjs': 'npm run build',
            'react': 'npm run build',
            'python': 'pip install -r requirements.txt',
            'docker': 'docker build -t {name} .',
            'static': 'echo "No build needed"'
        }
        return commands.get(proj_type, 'npm run build')
    
    def _detect_output_dir(self, proj_type: str) -> str:
        """Detecta diretório de saída baseado no tipo"""
        dirs = {
            'nextjs': '.next',
            'react': 'dist',
            'python': '.',
            'docker': '.',
            'static': '.'
        }
        return dirs.get(proj_type, 'dist')
    
    def refresh(self):
        """Rescaneia projetos"""
        self.projects.clear()
        self._scan_projects()


# Singleton global
_registry = None

def get_registry() -> ProjectRegistry:
    """Retorna instância global do registro"""
    global _registry
    if _registry is None:
        _registry = ProjectRegistry()
    return _registry


if __name__ == "__main__":
    # Teste
    registry = ProjectRegistry()
    print("📁 Projetos encontrados:")
    for proj in registry.list_projects():
        print(f"  - {proj['name']} ({proj['type']} → {proj['platform']})")
