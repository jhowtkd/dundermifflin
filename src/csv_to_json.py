#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Conversão CSV para JSON

Este módulo fornece funcionalidades robustas para converter arquivos CSV
em formato JSON, com suporte a múltiplos formatos, validações e tratamento
de erros completo.

Autor: Dev Team
Versão: 1.0.0
"""

import csv
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSVToJSONError(Exception):
    """Exceção base para erros de conversão CSV para JSON."""
    pass


class FileNotFoundError(CSVToJSONError):
    """Erro quando o arquivo CSV não é encontrado."""
    pass


class InvalidCSVError(CSVToJSONError):
    """Erro quando o formato do CSV é inválido."""
    pass


class EncodingError(CSVToJSONError):
    """Erro relacionado a encoding do arquivo."""
    pass


@dataclass
class ConversionConfig:
    """
    Configuração para conversão CSV para JSON.
    
    Attributes:
        delimiter: Caractere delimitador de campos (default: ',')
        quotechar: Caractere de citação (default: '"')
        encoding: Encoding do arquivo (default: 'utf-8')
        skip_empty_rows: Pular linhas vazias (default: True)
        skip_empty_columns: Pular colunas vazias (default: False)
        trim_whitespace: Remover espaços em branco (default: True)
        null_values: Lista de valores que devem ser tratados como null
        type_inference: Inferir tipos de dados automaticamente (default: True)
        batch_size: Tamanho do lote para processamento de arquivos grandes
    """
    delimiter: str = ','
    quotechar: str = '"'
    encoding: str = 'utf-8'
    skip_empty_rows: bool = True
    skip_empty_columns: bool = False
    trim_whitespace: bool = True
    null_values: Optional[List[str]] = None
    type_inference: bool = True
    batch_size: Optional[int] = None
    
    def __post_init__(self):
        if self.null_values is None:
            self.null_values = ['', 'NULL', 'null', 'N/A', 'n/a', '-', 'NaN']


@dataclass
class ConversionResult:
    """
    Resultado da conversão CSV para JSON.
    
    Attributes:
        data: Lista de dicionários representando os registros
        total_rows: Número total de linhas processadas
        total_columns: Número de colunas
        columns: Lista de nomes das colunas
        errors: Lista de erros encontrados durante a conversão
        warnings: Lista de avisos gerados
    """
    data: List[Dict[str, Any]]
    total_rows: int
    total_columns: int
    columns: List[str]
    errors: List[str]
    warnings: List[str]
    
    def to_json(self, indent: Optional[int] = 2, 
                sort_keys: bool = False) -> str:
        """
        Converte o resultado para string JSON formatada.
        
        Args:
            indent: Número de espaços para indentação
            sort_keys: Ordenar chaves do JSON
            
        Returns:
            String JSON formatada
        """
        return json.dumps(
            self.data,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=False
        )
    
    def save_to_file(self, output_path: Union[str, Path], 
                     indent: Optional[int] = 2) -> Path:
        """
        Salva o resultado em arquivo JSON.
        
        Args:
            output_path: Caminho do arquivo de saída
            indent: Número de espaços para indentação
            
        Returns:
            Path do arquivo salvo
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"JSON salvo em: {output_path}")
        return output_path


def _infer_type(value: str) -> Any:
    """
    Infere o tipo de dado de uma string.
    
    Tenta converter para int, float, bool ou mantém como string.
    
    Args:
        value: Valor string a ser convertido
        
    Returns:
        Valor convertido para o tipo apropriado
    """
    if value is None:
        return None
    
    # Booleanos
    lower_val = value.lower()
    if lower_val in ('true', 'yes', '1', 'sim'):
        return True
    if lower_val in ('false', 'no', '0', 'não', 'nao'):
        return False
    
    # Inteiro
    try:
        if '.' not in value and 'e' not in value.lower():
            return int(value)
    except ValueError:
        pass
    
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Manter como string
    return value


def _clean_value(value: str, config: ConversionConfig) -> Any:
    """
    Limpa e processa um valor individual.
    
    Args:
        value: Valor string do CSV
        config: Configuração de conversão
        
    Returns:
        Valor processado
    """
    if value is None:
        return None
    
    # Trim whitespace
    if config.trim_whitespace:
        value = value.strip()
    
    # Verificar valores nulos
    if value in config.null_values:
        return None
    
    # Inferir tipo
    if config.type_inference:
        return _infer_type(value)
    
    return value


def _clean_headers(headers: List[str], config: ConversionConfig) -> List[str]:
    """
    Limpa e valida os cabeçalhos do CSV.
    
    Args:
        headers: Lista de cabeçalhos brutos
        config: Configuração de conversão
        
    Returns:
        Lista de cabeçalhos limpos
    """
    cleaned = []
    seen = set()
    
    for i, header in enumerate(headers):
        # Limpar espaços
        if config.trim_whitespace:
            header = header.strip()
        
        # Coluna vazia
        if not header:
            if config.skip_empty_columns:
                continue
            header = f"column_{i}"
        
        # Cabeçalhos duplicados
        original = header
        counter = 1
        while header in seen:
            header = f"{original}_{counter}"
            counter += 1
        
        seen.add(header)
        cleaned.append(header)
    
    return cleaned


def convert_csv_to_json(
    input_path: Union[str, Path],
    config: Optional[ConversionConfig] = None,
    row_transformer: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
) -> ConversionResult:
    """
    Converte um arquivo CSV para estrutura de dados JSON.
    
    Esta é a função principal do módulo. Ela lê um arquivo CSV e converte
    para uma lista de dicionários que pode ser serializada como JSON.
    
    Args:
        input_path: Caminho do arquivo CSV de entrada
        config: Configuração opcional de conversão
        row_transformer: Função opcional para transformar cada linha
        
    Returns:
        ConversionResult contendo os dados convertidos e metadados
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
        InvalidCSVError: Se o CSV estiver mal formatado
        EncodingError: Se houver problemas de encoding
        
    Example:
        >>> result = convert_csv_to_json('dados.csv')
        >>> print(result.to_json())
        >>> result.save_to_file('saida.json')
        
        >>> # Com configuração customizada
        >>> config = ConversionConfig(delimiter=';', encoding='latin1')
        >>> result = convert_csv_to_json('dados.csv', config)
    """
    input_path = Path(input_path)
    config = config or ConversionConfig()
    
    # Verificar arquivo
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
    
    if not input_path.is_file():
        raise FileNotFoundError(f"Caminho não é um arquivo: {input_path}")
    
    logger.info(f"Iniciando conversão: {input_path}")
    
    data: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    columns: List[str] = []
    row_count = 0
    
    try:
        with open(input_path, 'r', encoding=config.encoding, newline='') as f:
            # Detectar se há BOM e pular
            first_char = f.read(1)
            if first_char != '\ufeff':
                f.seek(0)
            else:
                logger.debug("BOM detectado e removido")
            
            # Criar reader CSV
            reader = csv.reader(
                f,
                delimiter=config.delimiter,
                quotechar=config.quotechar
            )
            
            # Ler cabeçalhos
            try:
                raw_headers = next(reader)
            except StopIteration:
                raise InvalidCSVError("Arquivo CSV está vazio")
            
            columns = _clean_headers(raw_headers, config)
            
            if not columns:
                raise InvalidCSVError("Nenhuma coluna encontrada no CSV")
            
            logger.debug(f"Colunas detectadas: {columns}")
            
            # Processar linhas
            for line_num, row in enumerate(reader, start=2):
                try:
                    # Pular linhas vazias
                    if config.skip_empty_rows and not any(row):
                        continue
                    
                    # Verificar número de colunas
                    if len(row) != len(columns):
                        warnings.append(
                            f"Linha {line_num}: número de colunas mismatch "
                            f"(esperado: {len(columns)}, encontrado: {len(row)})"
                        )
                    
                    # Criar dicionário da linha
                    row_dict: Dict[str, Any] = {}
                    for i, col_name in enumerate(columns):
                        if i < len(row):
                            row_dict[col_name] = _clean_value(row[i], config)
                        else:
                            row_dict[col_name] = None
                    
                    # Aplicar transformador se fornecido
                    if row_transformer:
                        try:
                            row_dict = row_transformer(row_dict)
                        except Exception as e:
                            errors.append(f"Linha {line_num}: erro no transformador: {e}")
                            continue
                    
                    data.append(row_dict)
                    row_count += 1
                    
                    # Log de progresso para arquivos grandes
                    if row_count % 10000 == 0:
                        logger.info(f"Processadas {row_count} linhas...")
                    
                except Exception as e:
                    errors.append(f"Linha {line_num}: {str(e)}")
                    logger.warning(f"Erro na linha {line_num}: {e}")
    
    except UnicodeDecodeError as e:
        raise EncodingError(
            f"Erro de encoding ao ler o arquivo. "
            f"Tente usar encoding='latin1' ou encoding='cp1252'. "
            f"Erro original: {e}"
        )
    except csv.Error as e:
        raise InvalidCSVError(f"Erro no formato CSV: {e}")
    except Exception as e:
        raise CSVToJSONError(f"Erro inesperado: {e}")
    
    logger.info(f"Conversão concluída: {row_count} linhas, {len(columns)} colunas")
    
    return ConversionResult(
        data=data,
        total_rows=row_count,
        total_columns=len(columns),
        columns=columns,
        errors=errors,
        warnings=warnings
    )


def convert_csv_string_to_json(
    csv_content: str,
    config: Optional[ConversionConfig] = None,
    row_transformer: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
) -> ConversionResult:
    """
    Converte conteúdo CSV em string para JSON.
    
    Útil quando o CSV está em memória ou vem de outra fonte.
    
    Args:
        csv_content: String contendo o conteúdo CSV
        config: Configuração opcional de conversão
        row_transformer: Função opcional para transformar cada linha
        
    Returns:
        ConversionResult contendo os dados convertidos
        
    Example:
        >>> csv_text = "nome,idade\nJoão,30\nMaria,25"
        >>> result = convert_csv_string_to_json(csv_text)
        >>> print(result.data)
    """
    import io
    
    config = config or ConversionConfig()
    
    data: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    columns: List[str] = []
    row_count = 0
    
    try:
        f = io.StringIO(csv_content)
        reader = csv.reader(
            f,
            delimiter=config.delimiter,
            quotechar=config.quotechar
        )
        
        # Ler cabeçalhos
        try:
            raw_headers = next(reader)
        except StopIteration:
            raise InvalidCSVError("Conteúdo CSV está vazio")
        
        columns = _clean_headers(raw_headers, config)
        
        # Processar linhas
        for line_num, row in enumerate(reader, start=2):
            try:
                if config.skip_empty_rows and not any(row):
                    continue
                
                row_dict: Dict[str, Any] = {}
                for i, col_name in enumerate(columns):
                    if i < len(row):
                        row_dict[col_name] = _clean_value(row[i], config)
                    else:
                        row_dict[col_name] = None
                
                if row_transformer:
                    row_dict = row_transformer(row_dict)
                
                data.append(row_dict)
                row_count += 1
                
            except Exception as e:
                errors.append(f"Linha {line_num}: {str(e)}")
    
    except Exception as e:
        raise CSVToJSONError(f"Erro na conversão: {e}")
    
    return ConversionResult(
        data=data,
        total_rows=row_count,
        total_columns=len(columns),
        columns=columns,
        errors=errors,
        warnings=warnings
    )


def batch_convert(
    input_paths: List[Union[str, Path]],
    output_dir: Union[str, Path],
    config: Optional[ConversionConfig] = None,
    file_pattern: str = "{stem}.json"
) -> Dict[str, ConversionResult]:
    """
    Converte múltiplos arquivos CSV em lote.
    
    Args:
        input_paths: Lista de caminhos de arquivos CSV
        output_dir: Diretório de saída para os arquivos JSON
        config: Configuração opcional de conversão
        file_pattern: Padrão para nomear arquivos de saída
        
    Returns:
        Dicionário mapeando caminho do arquivo para ConversionResult
        
    Example:
        >>> arquivos = ['dados1.csv', 'dados2.csv']
        >>> resultados = batch_convert(arquivos, './saida/')
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for input_path in input_paths:
        input_path = Path(input_path)
        
        try:
            result = convert_csv_to_json(input_path, config)
            
            # Gerar nome de saída
            output_name = file_pattern.format(
                stem=input_path.stem,
                name=input_path.name
            )
            output_path = output_dir / output_name
            
            result.save_to_file(output_path)
            results[str(input_path)] = result
            
        except Exception as e:
            logger.error(f"Erro ao converter {input_path}: {e}")
            results[str(input_path)] = ConversionResult(
                data=[],
                total_rows=0,
                total_columns=0,
                columns=[],
                errors=[str(e)],
                warnings=[]
            )
    
    return results


# Funções utilitárias adicionais

def detect_delimiter(file_path: Union[str, Path], 
                     encoding: str = 'utf-8') -> str:
    """
    Tenta detectar o delimitador de um arquivo CSV.
    
    Args:
        file_path: Caminho do arquivo CSV
        encoding: Encoding do arquivo
        
    Returns:
        Delimitador detectado (',', ';', '\t', etc.)
    """
    delimiters = [',', ';', '\t', '|']
    counts = {d: 0 for d in delimiters}
    
    with open(file_path, 'r', encoding=encoding) as f:
        # Ler primeiras 5 linhas para análise
        for _ in range(5):
            line = f.readline()
            if not line:
                break
            for delim in delimiters:
                counts[delim] += line.count(delim)
    
    # Retornar delimitador com mais ocorrências
    return max(counts, key=counts.get)


def validate_csv(file_path: Union[str, Path],
                 config: Optional[ConversionConfig] = None) -> Dict[str, Any]:
    """
    Valida a estrutura de um arquivo CSV sem converter.
    
    Args:
        file_path: Caminho do arquivo CSV
        config: Configuração opcional
        
    Returns:
        Dicionário com informações de validação
    """
    config = config or ConversionConfig()
    
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'total_rows': 0,
        'total_columns': 0,
        'columns': []
    }
    
    try:
        with open(file_path, 'r', encoding=config.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=config.delimiter)
            
            try:
                headers = next(reader)
                result['columns'] = _clean_headers(headers, config)
                result['total_columns'] = len(result['columns'])
            except StopIteration:
                result['valid'] = False
                result['errors'].append("Arquivo vazio")
                return result
            
            for line_num, row in enumerate(reader, start=2):
                result['total_rows'] += 1
                
                if len(row) != len(result['columns']):
                    result['warnings'].append(
                        f"Linha {line_num}: número de colunas inconsistente"
                    )
    
    except Exception as e:
        result['valid'] = False
        result['errors'].append(str(e))
    
    return result


if __name__ == '__main__':
    # Exemplo de uso
    print("=" * 50)
    print("CSV to JSON Converter - Exemplo de Uso")
    print("=" * 50)
    
    # Exemplo 1: Conversão básica de string
    csv_exemplo = """nome,idade,cidade,salario,ativo
João Silva,30,São Paulo,4500.50,Sim
Maria Santos,25,Rio de Janeiro,5200.00,Sim
Pedro Costa,35,Belo Horizonte,NULL,Não
Ana Oliveira,28,Curitiba,3800.75,Sim"""
    
    print("\n1. Conversão básica de CSV string:")
    result = convert_csv_string_to_json(csv_exemplo)
    print(result.to_json())
    
    # Exemplo 2: Com transformador customizado
    print("\n2. Com transformador de dados:")
    
    def transformar_dados(row: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona campo calculado."""
        row['faixa_salarial'] = 'Alta' if row.get('salario', 0) > 4000 else 'Baixa'
        return row
    
    result = convert_csv_string_to_json(csv_exemplo, row_transformer=transformar_dados)
    print(result.to_json())
    
    print("\n✅ Módulo carregado com sucesso!")
    print("\nFunções disponíveis:")
    print("  - convert_csv_to_json(): Conversão de arquivo")
    print("  - convert_csv_string_to_json(): Conversão de string")
    print("  - batch_convert(): Conversão em lote")
    print("  - detect_delimiter(): Detectar delimitador")
    print("  - validate_csv(): Validar estrutura CSV")
