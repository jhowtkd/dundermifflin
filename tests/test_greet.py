#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários para a função greet

Cobertura:
- Saudação básica com nome
- Nome vazio
- Nome com espaços
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from greet import greet


class TestGreet(unittest.TestCase):
    """Testes para a função greet."""
    
    def test_greet_with_name(self):
        """Testa saudação com nome válido."""
        result = greet("João")
        self.assertEqual(result, "Olá, João!")
    
    def test_greet_with_another_name(self):
        """Testa saudação com outro nome."""
        result = greet("Maria")
        self.assertEqual(result, "Olá, Maria!")
    
    def test_greet_empty_string(self):
        """Testa saudação com string vazia."""
        result = greet("")
        self.assertEqual(result, "Olá, !")
    
    def test_greet_with_spaces(self):
        """Testa saudação com nome contendo espaços."""
        result = greet("João Silva")
        self.assertEqual(result, "Olá, João Silva!")


def run_tests():
    """Executa todos os testes."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
