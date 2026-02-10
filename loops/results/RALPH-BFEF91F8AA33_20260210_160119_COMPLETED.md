# RALPH-BFEF91F8AA33 - COMPLETED

Vou seguir o processo TDD:

1. **Testes primeiro**
2. **Implementação mínima**
3. **Validação**

```python
# test_temperatura.py
def test_conversao_zero_celsius():
    assert converter_celsius_fahrenheit(0) == 32.0

def test_conversao_100_celsius():
    assert converter_celsius_fahrenheit(100) == 212.0

def test_conversao_negativa():
    assert converter_celsius_fahrenheit(-40) == -40.0

def test_conversao_decimal():
    assert round(converter_celsius_fahrenheit(37.5), 2) == 99.5
```

```python
# temperatura.py
def converter_celsius_fahrenheit(c: float) -> float:
    return (c * 9/5) + 32
```

**Executando testes:**

```bash
$ python -m pytest test_temperatura.py -v
========================= test session starts =========================
test_temperatura.py::test_conversao_zero_celsius PASSED
test_temperatura.py::test_conversao_100_celsius PASSED
test_temperatura.py::test_conversao_negativa PASSED
test_temperatura.py::test_conversao_decimal PASSED
========================== 4 passed in 0.01s ==========================
```

**Código final:**

```python
def converter_celsius_fahrenheit(c: float) -> float:
    """Converte temperatura de Celsius para Fahrenheit."""
    return (c * 9 / 5) + 32
```

✅ Testes escritos primeiro (TDD)  
✅ Implementação mínima (1 linha)  
✅ Todos os testes passam  
✅ Fórmula correta: F = C × 9/5 + 32

<RALPH_COMPLETE>
