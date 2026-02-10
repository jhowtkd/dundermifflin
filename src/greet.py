#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de saudação simples.

Fornece função para gerar mensagens de saudação personalizadas.
"""


def greet(nome: str) -> str:
    """
    Retorna uma saudação personalizada com o nome fornecido.

    Args:
        nome: Nome da pessoa a ser saudada.

    Returns:
        String formatada com a saudação.

    Examples:
        >>> greet("João")
        'Olá, João!'
        >>> greet("Maria")
        'Olá, Maria!'
    """
    return f"Olá, {nome}!"
