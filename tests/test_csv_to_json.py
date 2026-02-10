#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários para o módulo csv_to_json

Cobertura:
- Conversão básica CSV para JSON
- Tratamento de erros
- Configurações customizadas
- Validação de dados
- Casos edge cases
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from csv_to_json import (
    convert_csv_to_json,
    convert_csv_string_to_json,
    batch_convert,
    detect_delimiter,
    validate_csv,
    ConversionConfig,
    ConversionResult,
    FileNotFoundError,
    InvalidCSVError,
    EncodingError,
    CSVToJSONError
)


# Helper para verificar exceções personalizadas (podem ser wrapadas)
def _is_invalid_csv_error(exc):
    """Verifica se a exceção é InvalidCSVError (mesmo que wrapada)."""
    return isinstance(exc, (InvalidCSVError, CSVToJSONError)) and "vazio" in str(exc).lower()


class TestConversionConfig(unittest.TestCase):
    """Testes para a classe ConversionConfig."""
    
    def test_default_values(self):
        """Testa valores padrão da configuração."""
        config = ConversionConfig()
        self.assertEqual(config.delimiter, ',')
        self.assertEqual(config.quotechar, '"')
        self.assertEqual(config.encoding, 'utf-8')
        self.assertTrue(config.skip_empty_rows)
        self.assertFalse(config.skip_empty_columns)
        self.assertTrue(config.trim_whitespace)
        self.assertTrue(config.type_inference)
    
    def test_custom_values(self):
        """Testa configuração customizada."""
        config = ConversionConfig(
            delimiter=';',
            encoding='latin1',
            type_inference=False
        )
        self.assertEqual(config.delimiter, ';')
        self.assertEqual(config.encoding, 'latin1')
        self.assertFalse(config.type_inference)
    
    def test_null_values_default(self):
        """Testa valores nulos padrão."""
        config = ConversionConfig()
        expected_nulls = ['', 'NULL', 'null', 'N/A', 'n/a', '-', 'NaN']
        self.assertEqual(config.null_values, expected_nulls)


class TestConvertCSVString(unittest.TestCase):
    """Testes para conversão de string CSV."""
    
    def test_basic_conversion(self):
        """Testa conversão básica."""
        csv_content = "nome,idade\nJoão,30\nMaria,25"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertEqual(result.total_rows, 2)
        self.assertEqual(result.total_columns, 2)
        self.assertEqual(result.columns, ['nome', 'idade'])
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]['nome'], 'João')
        self.assertEqual(result.data[0]['idade'], 30)
    
    def test_type_inference_int(self):
        """Testa inferência de tipo inteiro."""
        csv_content = "id,valor\n1,100\n2,200"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertIsInstance(result.data[0]['id'], int)
        self.assertIsInstance(result.data[0]['valor'], int)
    
    def test_type_inference_float(self):
        """Testa inferência de tipo float."""
        csv_content = "produto,preco\nMaçã,2.50\nBanana,1.75"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertIsInstance(result.data[0]['preco'], float)
        self.assertEqual(result.data[0]['preco'], 2.50)
    
    def test_type_inference_bool(self):
        """Testa inferência de tipo booleano."""
        csv_content = "nome,ativo\nJoão,true\nMaria,false\nPedro,1\nAna,0"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertIsInstance(result.data[0]['ativo'], bool)
        self.assertTrue(result.data[0]['ativo'])
        self.assertFalse(result.data[1]['ativo'])
        self.assertTrue(result.data[2]['ativo'])
        self.assertFalse(result.data[3]['ativo'])
    
    def test_null_values(self):
        """Testa tratamento de valores nulos."""
        csv_content = "nome,idade\nJoão,30\nMaria,NULL\nPedro,-"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertEqual(result.data[0]['idade'], 30)
        self.assertIsNone(result.data[1]['idade'])
        self.assertIsNone(result.data[2]['idade'])
    
    def test_whitespace_trim(self):
        """Testa remoção de espaços em branco."""
        csv_content = "nome, cidade \n  João  ,  São Paulo  "
        result = convert_csv_string_to_json(csv_content)
        
        self.assertEqual(result.data[0]['nome'], 'João')
        self.assertEqual(result.data[0]['cidade'], 'São Paulo')
    
    def test_custom_delimiter(self):
        """Testa delimitador customizado."""
        csv_content = "nome;idade\nJoão;30\nMaria;25"
        config = ConversionConfig(delimiter=';')
        result = convert_csv_string_to_json(csv_content, config)
        
        self.assertEqual(result.total_rows, 2)
        self.assertEqual(result.data[0]['nome'], 'João')
        self.assertEqual(result.data[0]['idade'], 30)
    
    def test_empty_csv(self):
        """Testa erro em CSV vazio."""
        with self.assertRaises((InvalidCSVError, CSVToJSONError)):
            convert_csv_string_to_json("")
    
    def test_row_transformer(self):
        """Testa transformador de linhas."""
        csv_content = "nome,idade\nJoão,30\nMaria,25"
        
        def add_category(row):
            row['categoria'] = 'adulto' if row['idade'] >= 18 else 'menor'
            return row
        
        result = convert_csv_string_to_json(csv_content, row_transformer=add_category)
        
        self.assertEqual(result.data[0]['categoria'], 'adulto')
        self.assertEqual(result.data[1]['categoria'], 'adulto')
    
    def test_quoted_values(self):
        """Testa valores entre aspas."""
        csv_content = 'nome,descricao\nJoão,"Descrição com, vírgula"\nMaria,"Outra descrição"'
        result = convert_csv_string_to_json(csv_content)
        
        self.assertEqual(result.data[0]['descricao'], 'Descrição com, vírgula')


class TestConvertCSVFile(unittest.TestCase):
    """Testes para conversão de arquivo CSV."""
    
    def setUp(self):
        """Cria arquivos temporários para testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
    
    def tearDown(self):
        """Remove arquivos temporários."""
        for f in self.test_files:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(self.temp_dir)
    
    def create_test_file(self, content, encoding='utf-8', suffix='.csv'):
        """Helper para criar arquivo de teste."""
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir)
        self.test_files.append(path)
        with os.fdopen(fd, 'w', encoding=encoding) as f:
            f.write(content)
        return path
    
    def test_file_not_found(self):
        """Testa erro quando arquivo não existe."""
        with self.assertRaises(FileNotFoundError):
            convert_csv_to_json('/caminho/inexistente.csv')
    
    def test_basic_file_conversion(self):
        """Testa conversão básica de arquivo."""
        content = "nome,idade\nJoão,30\nMaria,25"
        path = self.create_test_file(content)
        
        result = convert_csv_to_json(path)
        
        self.assertEqual(result.total_rows, 2)
        self.assertEqual(result.data[0]['nome'], 'João')
    
    def test_latin1_encoding(self):
        """Testa encoding latin1."""
        content = "nome,cidade\nJoão,São Paulo\nJosé,Rio de Janeiro"
        path = self.create_test_file(content, encoding='latin1')
        
        config = ConversionConfig(encoding='latin1')
        result = convert_csv_to_json(path, config)
        
        self.assertEqual(result.data[0]['nome'], 'João')
    
    def test_skip_empty_rows(self):
        """Testa pulo de linhas vazias."""
        content = "nome,idade\nJoão,30\n\nMaria,25\n\n"
        path = self.create_test_file(content)
        
        result = convert_csv_to_json(path)
        
        self.assertEqual(result.total_rows, 2)
    
    def test_result_to_json(self):
        """Testa exportação para string JSON."""
        content = "nome,idade\nJoão,30"
        path = self.create_test_file(content)
        
        result = convert_csv_to_json(path)
        json_str = result.to_json()
        
        # Verificar se é JSON válido
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['nome'], 'João')
    
    def test_result_save_to_file(self):
        """Testa salvamento em arquivo."""
        content = "nome,idade\nJoão,30"
        path = self.create_test_file(content)
        
        result = convert_csv_to_json(path)
        output_path = Path(self.temp_dir) / 'output.json'
        saved_path = result.save_to_file(output_path)
        
        self.assertTrue(saved_path.exists())
        
        # Verificar conteúdo
        with open(saved_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data[0]['nome'], 'João')
        
        os.remove(saved_path)


class TestBatchConvert(unittest.TestCase):
    """Testes para conversão em lote."""
    
    def setUp(self):
        """Cria estrutura de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / 'output'
        self.test_files = []
        
        # Criar arquivos CSV de teste
        for i in range(3):
            content = f"id,nome\n{i},Arquivo{i}"
            path = Path(self.temp_dir) / f'test{i}.csv'
            path.write_text(content, encoding='utf-8')
            self.test_files.append(str(path))
    
    def tearDown(self):
        """Limpa arquivos de teste."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_batch_convert(self):
        """Testa conversão em lote."""
        results = batch_convert(self.test_files, self.output_dir)
        
        self.assertEqual(len(results), 3)
        
        # Verificar se arquivos foram criados
        for i in range(3):
            output_file = self.output_dir / f'test{i}.json'
            self.assertTrue(output_file.exists())


class TestDetectDelimiter(unittest.TestCase):
    """Testes para detecção de delimitador."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_comma(self):
        """Testa detecção de vírgula."""
        path = Path(self.temp_dir) / 'comma.csv'
        path.write_text("a,b,c\n1,2,3\n4,5,6")
        
        delim = detect_delimiter(path)
        self.assertEqual(delim, ',')
    
    def test_detect_semicolon(self):
        """Testa detecção de ponto-e-vírgula."""
        path = Path(self.temp_dir) / 'semicolon.csv'
        path.write_text("a;b;c\n1;2;3\n4;5;6")
        
        delim = detect_delimiter(path)
        self.assertEqual(delim, ';')
    
    def test_detect_tab(self):
        """Testa detecção de tab."""
        path = Path(self.temp_dir) / 'tab.csv'
        path.write_text("a\tb\tc\n1\t2\t3\n4\t5\t6")
        
        delim = detect_delimiter(path)
        self.assertEqual(delim, '\t')


class TestValidateCSV(unittest.TestCase):
    """Testes para validação de CSV."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_csv(self):
        """Testa validação de CSV válido."""
        path = Path(self.temp_dir) / 'valid.csv'
        path.write_text("nome,idade\nJoão,30\nMaria,25")
        
        result = validate_csv(path)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['total_rows'], 2)
        self.assertEqual(result['total_columns'], 2)
    
    def test_empty_csv_validation(self):
        """Testa validação de CSV vazio."""
        path = Path(self.temp_dir) / 'empty.csv'
        path.write_text("")
        
        result = validate_csv(path)
        
        self.assertFalse(result['valid'])
        self.assertIn("Arquivo vazio", result['errors'])


class TestEdgeCases(unittest.TestCase):
    """Testes para casos edge."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_duplicate_headers(self):
        """Testa tratamento de cabeçalhos duplicados."""
        csv_content = "nome,nome,idade\nJoão,João Silva,30"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertIn('nome', result.columns)
        self.assertIn('nome_1', result.columns)
    
    def test_empty_columns(self):
        """Testa colunas vazias."""
        csv_content = "nome,,idade\nJoão,teste,30"
        config = ConversionConfig(skip_empty_columns=True)
        result = convert_csv_string_to_json(csv_content, config)
        
        # Quando skip_empty_columns=True, a coluna vazia é removida
        # Então só temos 2 colunas: nome e idade
        self.assertEqual(len(result.columns), 2)
        self.assertIn('nome', result.columns)
        self.assertIn('idade', result.columns)
    
    def test_special_characters(self):
        """Testa caracteres especiais."""
        csv_content = "nome,descrição\nJoão,Descrição com acentuação: çãõü"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertEqual(result.data[0]['descrição'], 'Descrição com acentuação: çãõü')
    
    def test_very_long_values(self):
        """Testa valores muito longos."""
        long_text = "A" * 10000
        csv_content = f"id,descricao\n1,{long_text}"
        result = convert_csv_string_to_json(csv_content)
        
        self.assertEqual(result.data[0]['descricao'], long_text)
    
    def test_numeric_strings(self):
        """Testa strings que parecem números mas não são."""
        csv_content = "codigo,telefone\n001,5511999999999\n002,5511888888888"
        config = ConversionConfig(type_inference=False)
        result = convert_csv_string_to_json(csv_content, config)
        
        # Com type_inference=False, devem permanecer como strings
        self.assertIsInstance(result.data[0]['telefone'], str)


class TestConversionResult(unittest.TestCase):
    """Testes para a classe ConversionResult."""
    
    def test_to_json_indent(self):
        """Testa formatação JSON com indentação."""
        result = ConversionResult(
            data=[{'nome': 'João', 'idade': 30}],
            total_rows=1,
            total_columns=2,
            columns=['nome', 'idade'],
            errors=[],
            warnings=[]
        )
        
        json_str = result.to_json(indent=4)
        self.assertIn('\n', json_str)
        self.assertIn('    ', json_str)
    
    def test_to_json_no_indent(self):
        """Testa formatação JSON sem indentação."""
        result = ConversionResult(
            data=[{'nome': 'João'}],
            total_rows=1,
            total_columns=1,
            columns=['nome'],
            errors=[],
            warnings=[]
        )
        
        json_str = result.to_json(indent=None)
        self.assertNotIn('\n  ', json_str)


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
