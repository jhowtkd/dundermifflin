"""Calcula média de uma lista de notas com tratamento de erro."""


def calcular_media(notas: list[float]) -> float:
    """
    Calcula a média aritmética de uma lista de notas.
    
    Args:
        notas: Lista de números (floats/int)
    
    Returns:
        float: Média das notas, ou 0.0 se lista vazia
    
    Raises:
        TypeError: Se notas não for uma lista
        ValueError: Se algum elemento não for numérico
    """
    if not isinstance(notas, list):
        raise TypeError("notas deve ser uma lista")
    
    if len(notas) == 0:
        return 0.0
    
    for nota in notas:
        if not isinstance(nota, (int, float)):
            raise ValueError("Todas as notas devem ser números")
    
    return sum(notas) / len(notas)
