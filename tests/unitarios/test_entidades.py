# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta, date
from decimal import Decimal

import mock

from pagador_boleto import entidades


class BoletoConfiguracaoMeioPagamento(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BoletoConfiguracaoMeioPagamento, self).__init__(*args, **kwargs)
        self.campos = ['ativo', 'valor_minimo_aceitado', 'desconto', 'desconto_valor', 'aplicar_no_total', 'json']
        self.codigo_gateway = 8

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_ter_os_campos_especificos_na_classe(self):
        entidades.ConfiguracaoMeioPagamento(234).campos.should.be.equal(self.campos)

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_ter_codigo_gateway(self):
        entidades.ConfiguracaoMeioPagamento(234).codigo_gateway.should.be.equal(self.codigo_gateway)

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', autospec=True)
    def test_deve_preencher_gateway_na_inicializacao(self, preencher_mock):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        preencher_mock.assert_called_with(configuracao, self.codigo_gateway, self.campos)

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_definir_formulario_na_inicializacao(self):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.formulario.should.be.a('pagador_boleto.cadastro.FormularioBoleto')

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_nao_ser_aplicacao(self):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.eh_aplicacao.should.be.falsy

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_ter_json_padrao_se_nao_tiver_ainda(self):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.json.should.be.equal(entidades.cadastro.BOLETO_BASE)

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_dizer_que_nao_estah_configurado_se_json_for_none(self):
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.json = None
        configuracao.configurado.should.be.falsy

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_dizer_que_nao_estah_configurado_se_for_tudo_none(self):
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

    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    def test_deve_dizer_que_estah_configurado(self):
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

    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', autospec=True)
    def test_definir_carteiras(self, carteira_mock):
        carteira = mock.MagicMock()
        carteira.listar_ativas.return_value = [
            mock.MagicMock(**{'convenio': True, 'nome': 'Nome 1', 'numero': '111', 'banco_nome': 'Banco A', 'banco_id': 10, 'ativo': True, 'id': 1}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 2', 'numero': '222', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': False, 'id': 2})
        ]
        carteira_mock.return_value = carteira
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.carteiras.should.be.equal([{'id': 1, 'numero': '111', 'nome': 'Nome 1'}, {'id': 2, 'numero': '222', 'nome': 'Nome 2'}])

    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', autospec=True)
    def test_definir_bancos(self, carteira_mock):
        carteira = mock.MagicMock()
        carteira.listar_ativas.return_value = [
            mock.MagicMock(**{'convenio': True, 'nome': 'Nome 1', 'numero': '111', 'banco_nome': 'Banco A', 'banco_id': 10, 'ativo': True, 'id': 1}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 2', 'numero': '222', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': False, 'id': 2})
        ]
        carteira_mock.return_value = carteira
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.bancos.should.be.equal([{'id': 10, 'nome': 'Banco A'}, {'id': 20, 'nome': 'Banco B'}])

    @mock.patch('pagador_boleto.entidades.ConfiguracaoMeioPagamento.preencher_gateway', mock.MagicMock())
    @mock.patch('pagador_boleto.entidades.entidades.CarteiraParaBoleto', autospec=True)
    def test_definir_banco_carteira(self, carteira_mock):
        carteira = mock.MagicMock()
        carteira.listar_ativas.return_value = [
            mock.MagicMock(**{'convenio': True, 'nome': 'Nome 1', 'numero': '111', 'banco_nome': 'Banco A', 'banco_id': 10, 'ativo': True, 'id': 1}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 2', 'numero': '222', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': True, 'id': 2}),
            mock.MagicMock(**{'convenio': False, 'nome': 'Nome 3', 'numero': '333', 'banco_nome': 'Banco B', 'banco_id': 20, 'ativo': True, 'id': 3})
        ]
        carteira_mock.return_value = carteira
        configuracao = entidades.ConfiguracaoMeioPagamento(234)
        configuracao.banco_carteira.should.be.equal({'10': {'1': {'convenio': True, 'nome': 'Nome 1'}}, '20': {'2': {'convenio': False, 'nome': 'Nome 2'}, '3': {'convenio': False, 'nome': 'Nome 3'}}})


class BoletoMontandoMalote(unittest.TestCase):
    def setUp(self):
        dados_json = {
            'empresa_beneficiario': 'Beneficiario', 'empresa_cnpj': '12345678901', 'empresa_estado': 'RJ', 'empresa_endereco': u'Endereço Empresa', 'empresa_cidade': 'Rio de Janeiro',
            'banco': '1',
            'carteira': '2',
            'banco_agencia': '1234', 'banco_conta': '234456', 'banco_convenio': None,
            'linha_1': 'LINHA 1',
            'linha_2': None,
            'linha_3': None,
        }
        carteiras = [{'id': i, 'nome': 'Carteira {}'.format(i), 'numero': 111 * i} for i in range(1, 4)]
        bancos = [{'id': i, 'nome': 'Banco {}'.format(i)} for i in range(1, 5)]
        self.loja_id = 23
        self.malote = entidades.Malote(mock.MagicMock(loja_id=self.loja_id, json=dados_json, bancos=bancos, carteiras=carteiras))
        self.pedido = mock.MagicMock()
        self.pedido.codigo_meio_pagamento = 'boleto'
        self.pedido.data_criacao = datetime(2015, 2, 28)
        self.data_documento = self.data_processamento = datetime(2015, 2, 28).date()
        self.data_vencimento = datetime(2015, 2, 28).date() + timedelta(days=5)
        self.pedido.valor_total = Decimal('100.40')
        self.pedido.numero = 1234
        self.pedido.endereco_pagamento = {
            'complemento': 'complemento',
            'endereco': u'Endereço', 'numero': 23,
            'bairro': 'Bairro', 'cidade': 'Cidade',
            'estado': 'MG', 'cep': '33555666'
        }
        self.pedido.endereco_entrega = {
            'nome': 'Cliente entrega',
            'complemento': 'complemento',
            'endereco': u'Endereço', 'numero': 23,
            'bairro': 'Bairro', 'cidade': 'Cidade',
            'estado': 'MG', 'cep': '33555666'
        }

    def test_deve_ter_propriedades(self):
        entidades.Malote('configuracao').to_dict().should.be.equal({
            'banco_agencia': None, 'banco_conta': None, 'banco_convenio': None, 'banco_nome': None, 'carteira_numero': None,
            'data_documento': None, 'data_processamento': None, 'data_vencimento': None,
            'empresa_beneficiario': None, 'empresa_cidade': None, 'empresa_cnpj': None, 'empresa_endereco': None, 'empresa_estado': None,
            'formato': 'linha_digitavel',
            'linha_1': '', 'linha_2': '', 'linha_3': '',
            'nosso_numero': None, 'numero_documento': None, 'sacado': None, 'valor_documento': None
        })

    def test_monta_endereco_completo(self):
        self.malote.endereco_completo(self.pedido).should.be.equal(u'Endereço, 23, complemento - Bairro, Cidade / MG - CEP: 33555666')

    def test_monta_conteudo(self):
        self.malote.monta_conteudo(self.pedido, {}, dados={'formato': 'html'})
        self.malote.to_dict().should.be.equal({'banco_agencia': '1234', 'banco_conta': '234456', 'banco_convenio': None, 'banco_nome': 'Banco 1', 'carteira_numero': 222, 'data_documento': date(2015, 2, 28), 'data_processamento': date(2015, 2, 28), 'data_vencimento': date(2015, 3, 5), 'empresa_beneficiario': 'Beneficiario', 'empresa_cidade': 'Rio de Janeiro', 'empresa_cnpj': '12345678901', 'empresa_endereco': 'Endere\xc3\xa7o Empresa', 'empresa_estado': 'RJ', 'formato': 'html', 'linha_1': 'LINHA 1', 'linha_2': '', 'linha_3': '', 'nosso_numero': None, 'numero_documento': 1234, 'sacado': ['Cliente entrega', 'Endere\xc3\xa7o, 23, complemento - Bairro, Cidade / MG - CEP: 33555666'], 'valor_documento': 100.4})

    def test_monta_conteudo_com_formato_invalido(self):
        self.malote.monta_conteudo(self.pedido, {}, dados={'formato': 'zas'})
        self.malote.to_dict().should.be.equal({'banco_agencia': '1234', 'banco_conta': '234456', 'banco_convenio': None, 'banco_nome': 'Banco 1', 'carteira_numero': 222, 'data_documento': date(2015, 2, 28), 'data_processamento': date(2015, 2, 28), 'data_vencimento': date(2015, 3, 5), 'empresa_beneficiario': 'Beneficiario', 'empresa_cidade': 'Rio de Janeiro', 'empresa_cnpj': '12345678901', 'empresa_endereco': 'Endere\xc3\xa7o Empresa', 'empresa_estado': 'RJ', 'formato': 'linha_digitavel', 'linha_1': 'LINHA 1', 'linha_2': '', 'linha_3': '', 'nosso_numero': None, 'numero_documento': 1234, 'sacado': ['Cliente entrega', 'Endere\xc3\xa7o, 23, complemento - Bairro, Cidade / MG - CEP: 33555666'], 'valor_documento': 100.4})

    def test_monta_conteudo_com_formato_padrao(self):
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        self.malote.to_dict().should.be.equal({'banco_agencia': '1234', 'banco_conta': '234456', 'banco_convenio': None, 'banco_nome': 'Banco 1', 'carteira_numero': 222, 'data_documento': date(2015, 2, 28), 'data_processamento': date(2015, 2, 28), 'data_vencimento': date(2015, 3, 5), 'empresa_beneficiario': 'Beneficiario', 'empresa_cidade': 'Rio de Janeiro', 'empresa_cnpj': '12345678901', 'empresa_endereco': 'Endere\xc3\xa7o Empresa', 'empresa_estado': 'RJ', 'formato': 'linha_digitavel', 'linha_1': 'LINHA 1', 'linha_2': '', 'linha_3': '', 'nosso_numero': None, 'numero_documento': 1234, 'sacado': ['Cliente entrega', 'Endere\xc3\xa7o, 23, complemento - Bairro, Cidade / MG - CEP: 33555666'], 'valor_documento': 100.4})

    def test_dah_erro_se_boleto_nao_tem_um_atributo(self):
        del self.malote.configuracao.json['banco_convenio']
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'A configuração do boleto para na loja {} não está preenchida corretamente.'.format(self.loja_id)
        )

    def test_dah_erro_se_boleto_nao_tem_um_atributo_em_caso_de_teste(self):
        del self.malote.configuracao.json['banco_convenio']
        self.pedido.numero = 10110011
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'Você precisa preencher e salvar as alterações antes de emitir um boleto de teste.'
        )

    def test_dah_erro_se_carteira_nao_for_encontrada(self):
        self.malote.configuracao.json['carteira'] = 10
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'A carteira id 10 definida para o boleto não foi encontrada ativa nas configurações da loja {}'.format(self.loja_id)
        )

    def test_dah_erro_se_carteira_nao_for_encontrada_em_caso_de_teste(self):
        self.malote.configuracao.json['carteira'] = 10
        self.pedido.numero = 10110011
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'Você precisa preencher e salvar as alterações antes de emitir um boleto de teste.'
        )

    def test_dah_erro_se_banco_nao_for_encontrado(self):
        self.malote.configuracao.json['banco'] = 10
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'O banco id 10 definido para o boleto não foi encontrado nas configurações da loja {}'.format(self.loja_id)
        )

    def test_dah_erro_se_banco_nao_for_encontrado_em_caso_de_teste(self):
        self.malote.configuracao.json['banco'] = 10
        self.pedido.numero = 10110011
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'Você precisa preencher e salvar as alterações antes de emitir um boleto de teste.'
        )

    def test_dah_erro_se_json_nao_for_encontrado(self):
        self.malote.configuracao.json = None
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'A configuração do boleto para na loja {} não está preenchida.'.format(self.loja_id)
        )

    def test_dah_erro_se_json_nao_for_encontrado_em_caso_de_teste(self):
        self.malote.configuracao.json = None
        self.pedido.numero = 10110011
        self.malote.monta_conteudo.when.called_with(self.pedido, {}, dados={}).should.throw(
            entidades.BoletoNaoGerado,
            u'Você precisa preencher e salvar as alterações antes de emitir um boleto de teste.'
        )
