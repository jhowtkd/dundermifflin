"""Calcula média de uma lista de notas."""


def calcular_media(notas: list[float]) -> float:
    """Calcula a média aritmética de uma lista de notas.

    Args:
        notas: Lista de números (floats/int).

    Returns:
        Média das notas, ou 0.0 se lista vazia.

    Raises:
        TypeError: Se notas não for uma lista.
        ValueError: Se algum elemento não for numérico.
    """
    if not isinstance(notas, list):
        raise TypeError("notas deve ser uma lista")

    if not notas:
        return 0.0

    if not all(isinstance(n, (int, float)) for n in notas):
        raise ValueError("Todas as notas devem ser números")

    return sum(notas) / len(notas)
