#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplos Práticos de Uso do Módulo csv_to_json

Este arquivo demonstra diversos cenários de uso do conversor CSV para JSON.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from csv_to_json import (
    convert_csv_to_json,
    convert_csv_string_to_json,
    batch_convert,
    detect_delimiter,
    validate_csv,
    ConversionConfig,
)


def exemplo_1_basico():
    """Exemplo 1: Conversão mais simples possível."""
    print("=" * 60)
    print("EXEMPLO 1: Conversão Básica")
    print("=" * 60)
    
    csv_content = """nome,idade,cidade
João Silva,30,São Paulo
Maria Santos,25,Rio de Janeiro
Pedro Costa,35,Belo Horizonte"""
    
    result = convert_csv_string_to_json(csv_content)
    
    print(f"Total de linhas: {result.total_rows}")
    print(f"Colunas: {result.columns}")
    print("\nJSON resultante:")
    print(result.to_json())


def exemplo_2_tipos_dados():
    """Exemplo 2: Inferência automática de tipos."""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Inferência de Tipos")
    print("=" * 60)
    
    csv_content = """produto,preco,quantidade,disponivel,data
Notebook,4500.00,10,true,2024-01-15
Mouse,89.90,50,true,2024-01-10
Teclado,NULL,0,false,2024-01-05"""
    
    result = convert_csv_string_to_json(csv_content)
    
    print("Tipos inferidos:")
    for row in result.data:
        print(f"  {row['produto']}: preço={type(row['preco']).__name__}, "
              f"qtd={type(row['quantidade']).__name__}, "
              f"disp={type(row['disponivel']).__name__}")
    
    print("\nJSON:")
    print(result.to_json(indent=2))


def exemplo_3_delimitador_customizado():
    """Exemplo 3: Usando delimitador diferente."""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: CSV com Ponto-e-Vírgula")
    print("=" * 60)
    
    # CSV no formato brasileiro (ponto-e-vírgula)
    csv_content = """nome;idade;salario
João Silva;30;R$ 5.000,00
Maria Santos;25;R$ 4.500,00
Pedro Costa;35;R$ 7.000,00"""
    
    config = ConversionConfig(
        delimiter=';',
        type_inference=False  # Manter salário como string
    )
    
    result = convert_csv_string_to_json(csv_content, config)
    print(result.to_json(indent=2))


def exemplo_4_transformacao_dados():
    """Exemplo 4: Transformação de dados durante conversão."""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Transformação de Dados")
    print("=" * 60)
    
    csv_content = """nome,nota1,nota2,nota3
João Silva,8.5,7.0,9.0
Maria Santos,9.0,8.5,9.5
Pedro Costa,6.0,5.5,7.0"""
    
    # Função para calcular média e situação
    def calcular_media(row):
        notas = [row['nota1'], row['nota2'], row['nota3']]
        media = sum(notas) / len(notas)
        row['media'] = round(media, 2)
        row['situacao'] = 'Aprovado' if media >= 7 else 'Recuperação'
        return row
    
    result = convert_csv_string_to_json(csv_content, row_transformer=calcular_media)
    
    print("Boletim com médias calculadas:")
    for aluno in result.data:
        print(f"  {aluno['nome']}: média={aluno['media']}, "
              f"situação={aluno['situacao']}")
    
    print("\nJSON completo:")
    print(result.to_json(indent=2))


def exemplo_5_validacao():
    """Exemplo 5: Validação de CSV antes da conversão."""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Validação de CSV")
    print("=" * 60)
    
    # CSV válido
    csv_valido = """nome,email,telefone
João,joao@email.com,11999999999
Maria,maria@email.com,11888888888"""
    
    # CSV com problemas
    csv_problematico = """nome,email
João,joao@email.com,extra_column
Maria"""
    
    print("Validando CSV válido:")
    result_valido = convert_csv_string_to_json(csv_valido)
    print(f"  Erros: {result_valido.errors}")
    print(f"  Avisos: {result_valido.warnings}")
    
    print("\nValidando CSV problemático:")
    result_problema = convert_csv_string_to_json(csv_problematico)
    print(f"  Erros: {result_problema.errors}")
    print(f"  Avisos: {result_problema.warnings}")


def exemplo_6_lote():
    """Exemplo 6: Conversão em lote (simulado)."""
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Conversão em Lote (Simulado)")
    print("=" * 60)
    
    # Simular múltiplos CSVs
    csvs = {
        'clientes': """id,nome,email
1,João,joao@email.com
2,Maria,maria@email.com""",
        'produtos': """id,nome,preco
1,Notebook,4500.00
2,Mouse,89.90""",
        'vendas': """id,cliente_id,produto_id,quantidade
1,1,1,2
2,2,2,5"""
    }
    
    print("Processando múltiplas tabelas:")
    resultados = {}
    for nome, conteudo in csvs.items():
        result = convert_csv_string_to_json(conteudo)
        resultados[nome] = result
        print(f"  {nome}: {result.total_rows} registros")
    
    # Mostrar relação entre tabelas
    print("\nExemplo de relacionamento:")
    cliente = resultados['clientes'].data[0]
    venda = [v for v in resultados['vendas'].data 
             if v['cliente_id'] == cliente['id']][0]
    produto = [p for p in resultados['produtos'].data 
               if p['id'] == venda['produto_id']][0]
    
    print(f"  Cliente '{cliente['nome']}' comprou {venda['quantidade']}x "
          f"'{produto['nome']}'")


def exemplo_7_encoding():
    """Exemplo 7: Tratamento de encoding."""
    print("\n" + "=" * 60)
    print("EXEMPLO 7: Encoding e Caracteres Especiais")
    print("=" * 60)
    
    csv_content = """nome,descrição,preço
Café,Grãos selecionados,R$ 25,00
Chá,Ervas naturais,R$ 15,00
Açaí,Fruta típica,R$ 20,00"""
    
    result = convert_csv_string_to_json(csv_content)
    
    print("Dados com acentuação:")
    for item in result.data:
        print(f"  {item['nome']}: {item['descrição']}")


def exemplo_8_configuracao_avancada():
    """Exemplo 8: Configuração avançada."""
    print("\n" + "=" * 60)
    print("EXEMPLO 8: Configuração Avançada")
    print("=" * 60)
    
    csv_content = """ Nome , Idade , Cidade 
 João , 30 , São Paulo 
 , 25 , Rio de Janeiro 
Maria   , NULL , Belo Horizonte """
    
    # Configuração para dados "sujos"
    config = ConversionConfig(
        trim_whitespace=True,           # Remover espaços
        skip_empty_rows=True,           # Pular linhas vazias
        null_values=['NULL', '', '-'],  # Valores nulos
        type_inference=True
    )
    
    result = convert_csv_string_to_json(csv_content, config)
    
    print("Dados limpos:")
    print(f"  Linhas processadas: {result.total_rows}")
    print(f"  Avisos: {result.warnings}")
    print("\nJSON:")
    print(result.to_json(indent=2))


def main():
    """Executa todos os exemplos."""
    exemplos = [
        exemplo_1_basico,
        exemplo_2_tipos_dados,
        exemplo_3_delimitador_customizado,
        exemplo_4_transformacao_dados,
        exemplo_5_validacao,
        exemplo_6_lote,
        exemplo_7_encoding,
        exemplo_8_configuracao_avancada,
    ]
    
    for exemplo in exemplos:
        try:
            exemplo()
        except Exception as e:
            print(f"\n❌ Erro no exemplo: {e}")
    
    print("\n" + "=" * 60)
    print("Todos os exemplos concluídos!")
    print("=" * 60)


if __name__ == '__main__':
    main()
