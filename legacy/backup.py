#!/usr/bin/env python3
"""
Backup Simples e Robusto
========================
Script de backup de arquivos com princípios pragmáticos:
- Funciona > Perfeito
- Simplicidade > Complexidade  
- Testes são não-negociáveis
- Monitoramento = feature

Uso:
    python backup.py /origem /destino
    python backup.py --test  # roda testes
"""

import os
import sys
import shutil
import hashlib
import logging
import unittest
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple, Optional


# =============================================================================
# CONFIGURAÇÃO DE LOG (Monitoramento = feature)
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('backup')


# =============================================================================
# DATA CLASSES
# =============================================================================
@dataclass
class BackupResult:
    """Resultado da operação de backup."""
    success: bool
    files_copied: int
    files_skipped: int
    errors: List[str]
    duration_ms: float
    
    def __str__(self) -> str:
        status = "✓ OK" if self.success else "✗ FALHOU"
        return (f"Backup {status} | "
                f"Copiados: {self.files_copied} | "
                f"Pulados: {self.files_skipped} | "
                f"Erros: {len(self.errors)} | "
                f"Tempo: {self.duration_ms:.0f}ms")


# =============================================================================
# CORE FUNCTIONS (Simplicidade > Complexidade)
# =============================================================================

class BackupError(Exception):
    """Erro específico do backup."""
    pass


def calculate_hash(filepath: Path) -> str:
    """Calcula hash MD5 de um arquivo para verificar duplicatas."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def needs_copy(source: Path, dest: Path) -> bool:
    """
    Verifica se arquivo precisa ser copiado.
    Copia se: não existe no destino OU tamanho diferente OU data de modificação diferente.
    """
    if not dest.exists():
        return True
    
    if source.stat().st_size != dest.stat().st_size:
        return True
        
    if source.stat().st_mtime != dest.stat().st_mtime:
        return True
    
    return False


def backup_file(source: Path, dest: Path) -> Tuple[bool, Optional[str]]:
    """
    Copia um arquivo mantendo metadados.
    Retorna (sucesso, erro_msg).
    """
    try:
        # Garante que diretório destino existe
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copia arquivo
        shutil.copy2(source, dest)
        
        # Verifica integridade (tamanho)
        if source.stat().st_size != dest.stat().st_size:
            return False, f"Tamanho diferente após cópia: {source}"
        
        return True, None
        
    except Exception as e:
        return False, f"Erro ao copiar {source}: {e}"


def backup_directory(source_dir: str, dest_dir: str) -> BackupResult:
    """
    Executa backup completo de diretório.
    
    Args:
        source_dir: Diretório de origem
        dest_dir: Diretório de destino
        
    Returns:
        BackupResult com estatísticas da operação
    """
    import time
    start_time = time.time()
    
    source = Path(source_dir).resolve()
    dest = Path(dest_dir).resolve()
    
    # Validações básicas
    if not source.exists():
        raise BackupError(f"Origem não existe: {source}")
    
    if not source.is_dir():
        raise BackupError(f"Origem não é diretório: {source}")
    
    # Evita backup para dentro de si mesmo
    if dest in source.parents or dest == source:
        raise BackupError("Destino não pode estar dentro da origem")
    
    logger.info(f"Iniciando backup: {source} → {dest}")
    
    files_copied = 0
    files_skipped = 0
    errors: List[str] = []
    
    # Lista todos os arquivos
    all_files = list(source.rglob("*"))
    total_files = len([f for f in all_files if f.is_file()])
    
    logger.info(f"Total de arquivos encontrados: {total_files}")
    
    for file_path in all_files:
        if not file_path.is_file():
            continue
            
        # Calcula caminho relativo
        rel_path = file_path.relative_to(source)
        dest_path = dest / rel_path
        
        if needs_copy(file_path, dest_path):
            success, error = backup_file(file_path, dest_path)
            if success:
                files_copied += 1
                logger.debug(f"Copiado: {rel_path}")
            else:
                errors.append(error or "Erro desconhecido")
                logger.warning(f"Falha: {rel_path}")
        else:
            files_skipped += 1
            logger.debug(f"Pulado (igual): {rel_path}")
    
    duration = (time.time() - start_time) * 1000
    
    result = BackupResult(
        success=len(errors) == 0,
        files_copied=files_copied,
        files_skipped=files_skipped,
        errors=errors,
        duration_ms=duration
    )
    
    logger.info(str(result))
    return result


# =============================================================================
# TESTES (Testes são não-negociáveis)
# =============================================================================

class TestBackup(unittest.TestCase):
    """Testes unitários do módulo de backup."""
    
    def setUp(self):
        """Cria estrutura temporária para testes."""
        import tempfile
        self.test_dir = Path(tempfile.mkdtemp())
        self.source = self.test_dir / "source"
        self.dest = self.test_dir / "dest"
        self.source.mkdir()
        
    def tearDown(self):
        """Limpa arquivos temporários."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_needs_copy_new_file(self):
        """Arquivo novo deve ser copiado."""
        source = self.source / "test.txt"
        dest = self.dest / "test.txt"
        source.write_text("conteúdo")
        
        self.assertTrue(needs_copy(source, dest))
    
    def test_needs_copy_existing_equal(self):
        """Arquivo igual não deve ser copiado."""
        source = self.source / "test.txt"
        dest = self.dest / "test.txt"
        self.dest.mkdir(parents=True)
        
        source.write_text("conteúdo")
        dest.write_text("conteúdo")
        
        # Ajusta mtime para ser igual
        stat = source.stat()
        os.utime(dest, (stat.st_atime, stat.st_mtime))
        
        self.assertFalse(needs_copy(source, dest))
    
    def test_needs_copy_different_size(self):
        """Arquivo com tamanho diferente deve ser copiado."""
        source = self.source / "test.txt"
        dest = self.dest / "test.txt"
        self.dest.mkdir(parents=True)
        
        source.write_text("conteúdo novo")
        dest.write_text("velho")
        
        self.assertTrue(needs_copy(source, dest))
    
    def test_backup_file_success(self):
        """Backup de arquivo deve funcionar."""
        source = self.source / "test.txt"
        dest = self.dest / "test.txt"
        source.write_text("conteúdo de teste")
        
        success, error = backup_file(source, dest)
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertTrue(dest.exists())
        self.assertEqual(dest.read_text(), "conteúdo de teste")
    
    def test_backup_directory_complete(self):
        """Backup de diretório deve copiar todos os arquivos."""
        # Cria estrutura
        (self.source / "a.txt").write_text("A")
        (self.source / "subdir").mkdir()
        (self.source / "subdir" / "b.txt").write_text("B")
        
        result = backup_directory(str(self.source), str(self.dest))
        
        self.assertTrue(result.success)
        self.assertEqual(result.files_copied, 2)
        self.assertEqual(result.files_skipped, 0)
        self.assertTrue((self.dest / "a.txt").exists())
        self.assertTrue((self.dest / "subdir" / "b.txt").exists())
    
    def test_backup_skip_unchanged(self):
        """Backup deve pular arquivos não modificados."""
        (self.source / "a.txt").write_text("A")
        
        # Primeiro backup
        result1 = backup_directory(str(self.source), str(self.dest))
        self.assertEqual(result1.files_copied, 1)
        
        # Segundo backup (sem mudanças)
        result2 = backup_directory(str(self.source), str(self.dest))
        self.assertEqual(result2.files_copied, 0)
        self.assertEqual(result2.files_skipped, 1)
    
    def test_backup_invalid_source(self):
        """Deve falhar com origem inexistente."""
        with self.assertRaises(BackupError):
            backup_directory("/caminho/que/nao/existe", str(self.dest))
    
    def test_calculate_hash(self):
        """Hash deve ser consistente."""
        test_file = self.source / "test.txt"
        test_file.write_text("conteúdo")
        
        hash1 = calculate_hash(test_file)
        hash2 = calculate_hash(test_file)
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 32)  # MD5 = 32 chars


def run_tests():
    """Executa suite de testes."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBackup)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


# =============================================================================
# CLI
# =============================================================================

def main():
    """Entry point do script."""
    if len(sys.argv) == 2 and sys.argv[1] == '--test':
        return run_tests()
    
    if len(sys.argv) != 3:
        print(__doc__)
        print("\nUso: python backup.py <origem> <destino>")
        print("     python backup.py --test")
        return 1
    
    source, dest = sys.argv[1], sys.argv[2]
    
    try:
        result = backup_directory(source, dest)
        print(f"\n{result}")
        return 0 if result.success else 1
        
    except BackupError as e:
        logger.error(f"Erro: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Backup interrompido pelo usuário")
        return 130


if __name__ == '__main__':
    sys.exit(main())
