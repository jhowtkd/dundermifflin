import pytest
from calcular_media import calcular_media


def test_media_lista_vazia():
    """Deve retornar 0 para lista vazia"""
    assert calcular_media([]) == 0.0


def test_media_uma_nota():
    """Média de uma única nota é ela mesma"""
    assert calcular_media([5.0]) == 5.0


def test_media_duas_notas():
    """Média aritmética simples"""
    assert calcular_media([4.0, 6.0]) == 5.0


def test_media_multiplas_notas():
    """Média de várias notas"""
    assert calcular_media([10.0, 8.0, 6.0, 7.0]) == 7.75


def test_media_numeros_negativos():
    """Deve lidar com notas negativas"""
    assert calcular_media([-5.0, 5.0]) == 0.0


def test_media_decimais():
    """Precisão com decimais"""
    assert calcular_media([7.5, 8.5, 9.0]) == 8.333333333333334


def test_media_nao_lista():
    """Deve lançar TypeError se não receber lista"""
    with pytest.raises(TypeError, match="notas deve ser uma lista"):
        calcular_media("não é lista")


def test_media_elementos_nao_numericos():
    """Deve lançar ValueError se elemento não for número"""
    with pytest.raises(ValueError, match="Todas as notas devem ser números"):
        calcular_media([5.0, "dez", 7.0])
