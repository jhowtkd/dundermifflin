from greet import greet


def test_greet_retorna_saudacao_formatada():
    assert greet("Maria") == "Olá, Maria!"


def test_greet_aceita_nome_vazio():
    assert greet("") == "Olá, !"


def test_greet_aceita_nome_com_espacos():
    assert greet("João Silva") == "Olá, João Silva!"
