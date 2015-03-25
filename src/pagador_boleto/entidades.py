# -*- coding: utf-8 -*-
import datetime

from pagador import entidades
from pagador_boleto import cadastro

CODIGO_GATEWAY = 8
CODIGO_MEIO_PAGAMENTO = 'boleto'


class TipoBoleto(object):
    html = 'html'
    pdf = 'pdf'
    linha_digitavel = 'linha_digitavel'

    @classmethod
    def eh_valido(cls, formato):
        return formato in [prop for prop in dir(cls) if not prop.startswith('__')]


class BoletoNaoGerado(Exception):
    pass


class Malote(entidades.Malote):
    def __init__(self, configuracao):
        super(Malote, self).__init__(configuracao)
        self.data_processamento = None
        self.data_documento = None
        self.data_vencimento = None
        self.valor_documento = None
        self.sacado = None
        self.numero_documento = None
        self.nosso_numero = None
        self.formato = TipoBoleto.linha_digitavel
        self.sacado = None
        self.empresa_beneficiario = None
        self.empresa_cnpj = None
        self.empresa_estado = None
        self.empresa_endereco = None
        self.empresa_cidade = None
        self.banco_nome = None
        self.carteira_numero = None
        self.banco_agencia = None
        self.banco_conta = None
        self.banco_convenio = None
        self.linha_1 = ''
        self.linha_2 = ''
        self.linha_3 = ''

    def endereco_completo(self, pedido):
        complemento = pedido.endereco_pagamento['complemento'] or ''
        if complemento:
            complemento = u', {}'.format(complemento)
        return u'{}, {}{} - {}, {} / {} - CEP: {}'.format(
            pedido.endereco_pagamento['endereco'], pedido.endereco_pagamento['numero'], complemento, pedido.endereco_pagamento['bairro'],
            pedido.endereco_pagamento['cidade'], pedido.endereco_pagamento['estado'], pedido.endereco_pagamento['cep'])

    def _dispara_excecao(self, pedido, mensagem):
        if pedido.numero == 1011001100:
            mensagem = u'Você precisa preencher e salvar as alterações antes de emitir um boleto de teste.'
        raise BoletoNaoGerado(mensagem)

    def monta_conteudo(self, pedido, parametros_contrato=None, dados=None):
        if not self.configuracao.json:
            self._dispara_excecao(pedido, u'A configuração do boleto para na loja {} não está preenchida.'.format(self.configuracao.loja_id))
        try:
            self.banco_nome = [banco['nome'] for banco in self.configuracao.bancos if int(banco['id']) == int(self.configuracao.json['banco'])][0]
        except (ValueError, IndexError, TypeError):
            self._dispara_excecao(pedido, u'O banco id {} definido para o boleto não foi encontrado nas configurações da loja {}'.format(self.configuracao.json['banco'], self.configuracao.loja_id))
        try:
            self.carteira_numero = [carteira['numero'] for carteira in self.configuracao.carteiras if int(carteira['id']) == int(self.configuracao.json['carteira'])][0]
        except (ValueError, IndexError):
            self._dispara_excecao(pedido, u'A carteira id {} definida para o boleto não foi encontrada ativa nas configurações da loja {}'.format(self.configuracao.json['carteira'], self.configuracao.loja_id))

        try:
            for chave in cadastro.BOLETO_BASE:
                if hasattr(self, chave):
                    valor = self.configuracao.json[chave]
                    if chave.startswith('linha') and not valor:
                        valor = ''
                    setattr(self, chave, valor)
        except KeyError:
            self._dispara_excecao(pedido, u'A configuração do boleto para na loja {} não está preenchida corretamente.'.format(self.configuracao.loja_id))
        self.sacado = [pedido.endereco_entrega['nome'], self.endereco_completo(pedido)]
        self.formato = TipoBoleto.linha_digitavel
        if 'formato' in dados:
            self.formato = dados['formato']
        if not TipoBoleto.eh_valido(self.formato):
            self.formato = TipoBoleto.linha_digitavel
        self.data_processamento = pedido.data_criacao.date()
        self.data_documento = pedido.data_criacao.date()
        self.data_vencimento = pedido.data_criacao.date() + datetime.timedelta(days=5)
        self.valor_documento = pedido.valor_total
        self.numero_documento = pedido.numero


class ConfiguracaoMeioPagamento(entidades.ConfiguracaoMeioPagamento):

    def __init__(self, loja_id, codigo_pagamento=None, eh_listagem=False):
        self.campos = ['ativo', 'valor_minimo_aceitado', 'desconto', 'desconto_valor', 'aplicar_no_total', 'json']
        self.codigo_gateway = CODIGO_GATEWAY
        self.eh_gateway = True
        super(ConfiguracaoMeioPagamento, self).__init__(loja_id, codigo_pagamento, eh_listagem=eh_listagem)
        self.formulario = cadastro.FormularioBoleto()
        if not self.json:
            self.json = cadastro.BOLETO_BASE
        carteiras = entidades.CarteiraParaBoleto().listar_ativas()
        self.carteiras = [{'id': carteira.id, 'nome': carteira.nome, 'numero': carteira.numero} for carteira in carteiras]
        self.bancos = [{'id': banco[0], 'nome': banco[1]} for banco in set([(carteira.banco_id, carteira.banco_nome) for carteira in carteiras])]
        self.banco_carteira = {}
        for banco in self.bancos:
            _carteiras = [carteira for carteira in carteiras if carteira.banco_id == banco['id']]
            if _carteiras:
                banco_id = str(banco['id'])
                self.banco_carteira[banco_id] = {}
                for carteira in _carteiras:
                    self.banco_carteira[banco_id][str(carteira.id)] = {'nome': carteira.nome, 'convenio': carteira.convenio}

    @property
    def configurado(self):
        if not self.json:
            return False
        return (
            self.json['empresa_beneficiario'] is not None and
            self.json['empresa_cnpj'] is not None and
            self.json['empresa_estado'] is not None and
            self.json['empresa_endereco'] is not None and
            self.json['empresa_cidade'] is not None and
            self.json['banco'] is not None and
            self.json['carteira'] is not None and
            self.json['banco_agencia'] is not None and
            self.json['banco_conta'] is not None and
            self.json['banco_convenio'] is not None and
            self.json['linha_1'] is not None
        )
