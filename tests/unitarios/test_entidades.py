# -*- coding: utf-8 -*-
import unittest
import mock

from pagador_boleto.reloaded import entidades


class BoletoConfiguracaoMeioPagamento(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BoletoConfiguracaoMeioPagamento, self).__init__(*args, **kwargs)
        self.campos = ['ativo', 'valor_minimo_aceitado', 'desconto_valor', 'aplicar_no_total', 'json']
        self.codigo_gateway = 8

    def test_deve_ter_os_campos_especificos_na_classe(self):
        entidades.ConfiguracaoMeioPagamento._campos.should.be.equal(self.campos)

    def test_deve_ter_codigo_gateway(self):
        entidades.ConfiguracaoMeioPagamento._codigo_gateway.should.be.equal(self.codigo_gateway)

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_deve_preencher_do_gateway_na_inicializacao(self, preencher_mock, carteira_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        preencher_mock.assert_called_with(configuracao, self.codigo_gateway, self.campos)

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_deve_definir_formulario_na_inicializacao(self, preencher_mock, carteira_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.formulario.should.be.a('pagador_boleto.reloaded.cadastro.FormularioBoleto')

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_deve_nao_ser_aplicacao(self, preencher_mock, carteira_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.eh_aplicacao.should.be.falsy

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_deve_ter_json_padrao_se_nao_tiver_ainda(self, preencher_mock, carteira_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.json.should.be.equal(entidades.cadastro.BOLETO_BASE)

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_deve_dizer_que_esta_configurado(self, preencher_mock, carteira_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.json = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': None,
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        configuracao.configurado.should.be.falsy

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_deve_dizer_que_estah_configurado(self, preencher_mock, carteira_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.json = {
            'empresa_beneficiario': 'Nome Beneficiario',
            'empresa_cnpj': '12345678901',
            'empresa_estado': 'RJ',
            'empresa_endereco': 'Endereco',
            'empresa_cidade': 'Cidade',
            'banco': '341',
            'carteira': '18',
            'banco_agencia': '1234',
            'banco_conta': '12345',
            'banco_convenio': '1122',
            'linha_1': 'Linha 1',
            'linha_2': None,
            'linha_3': None,
        }
        configuracao.configurado.should.be.truthy

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_definir_carteiras(self, preencher_mock, carteira_mock):
        carteira = mock.MagicMock()
        carteira.listar_ativas.return_value = [
            mock.MagicMock(**{'convenio': True, 'nome': 'Nome 1', 'numero': '111', 'banco_nome': 'Banco A', 'banco_id': 10, 'ativo': True, 'id': 1}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 2', 'numero': '222', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': False, 'id': 2})
        ]
        carteira_mock.return_value = carteira
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.carteiras.should.be.equal([{'id': 1, 'nome': 'Nome 1'}, {'id': 2, 'nome': 'Nome 2'}])

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_definir_bancos(self, preencher_mock, carteira_mock):
        carteira = mock.MagicMock()
        carteira.listar_ativas.return_value = [
            mock.MagicMock(**{'convenio': True, 'nome': 'Nome 1', 'numero': '111', 'banco_nome': 'Banco A', 'banco_id': 10, 'ativo': True, 'id': 1}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 2', 'numero': '222', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': False, 'id': 2})
        ]
        carteira_mock.return_value = carteira
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.bancos.should.be.equal([{'id': 10, 'nome': 'Banco A'}, {'id': 20, 'nome': 'Banco B'}])

    @mock.patch('pagador_boleto.reloaded.entidades.entidades.CarteiraParaBoleto', autospec=True)
    @mock.patch('pagador_boleto.reloaded.entidades.ConfiguracaoMeioPagamento.preencher_do_gateway', autospec=True)
    def test_definir_banco_carteira(self, preencher_mock, carteira_mock):
        carteira = mock.MagicMock()
        carteira.listar_ativas.return_value = [
            mock.MagicMock(**{'convenio': True, 'nome': 'Nome 1', 'numero': '111', 'banco_nome': 'Banco A', 'banco_id': 10, 'ativo': True, 'id': 1}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 2', 'numero': '222', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': True, 'id': 2}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 3', 'numero': '333', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': True, 'id': 3})
        ]
        carteira_mock.return_value = carteira
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.banco_carteira.should.be.equal({'10': {'1': {'convenio': True, 'nome': 'Nome 1'}}, '20': {'2': {'convenio': False, 'nome': 'Nome 2'}, '3': {'convenio': False, 'nome': 'Nome 3'}}})
