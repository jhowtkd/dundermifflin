def fibonacci(n: int) -> list:
    """Retorna sequência de Fibonacci com n termos."""
    if n < 0:
        raise ValueError("n deve ser não-negativo")
    
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    
    return seq
