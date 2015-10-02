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


class Malote(entidades.Malote):
    def __init__(self, configuracao):
        super(Malote, self).__init__(configuracao)
        self.data_processamento = None
        self.data_documento = None
        self.data_vencimento = None
        self.valor_documento = None
        self.numero_documento = None
        self.nosso_numero = None
        self.formato = TipoBoleto.linha_digitavel
        self.dias_vencimento = 2
        self.sacado = None
        self.sacado_documento = None
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
        if pedido.numero == 236:
            mensagem = u'Você precisa preencher e salvar as alterações antes de emitir um boleto de teste.'
        raise self.DadosInvalidos(mensagem)

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
                    #TODO: este if é só para garantir que usuários atuais não tenha erro se o json deles não tiverem o dias_vencimento. Depois que normalizar, retirar
                    if chave == 'dias_vencimento':
                        valor = self.configuracao.json.get(chave, 2)
                    else:
                        valor = self.configuracao.json[chave]
                    if chave.startswith('linha') and not valor:
                        valor = ''
                    setattr(self, chave, valor)
        except KeyError:
            self._dispara_excecao(pedido, u'A configuração do boleto para na loja {} não está preenchida corretamente.'.format(self.configuracao.loja_id))
        self.sacado = [pedido.endereco_entrega['nome'], self.endereco_completo(pedido)]
        self.sacado_documento = pedido.cliente_documento
        self.formato = TipoBoleto.linha_digitavel
        if 'formato' in dados:
            self.formato = dados['formato']
        if not TipoBoleto.eh_valido(self.formato):
            self.formato = TipoBoleto.linha_digitavel
        self.data_processamento = pedido.data_criacao.date()
        self.data_documento = pedido.data_criacao.date()
        self.data_vencimento = pedido.data_criacao.date() + datetime.timedelta(days=int(self.dias_vencimento))
        self.valor_documento = pedido.valor_total
        self.numero_documento = pedido.numero


class ConfiguracaoMeioPagamento(entidades.ConfiguracaoMeioPagamento):
    modos_pagamento_aceitos = {
        'outros': ['boleto']
    }

    def __init__(self, loja_id, codigo_pagamento=None, eh_listagem=False):
        self.campos = ['ativo', 'valor_minimo_aceitado', 'desconto', 'desconto_valor', 'aplicar_no_total', 'json']
        self.codigo_gateway = CODIGO_GATEWAY
        self.eh_gateway = True
        super(ConfiguracaoMeioPagamento, self).__init__(loja_id, codigo_pagamento, eh_listagem=eh_listagem)
        if not self.eh_listagem:
            self.formulario = cadastro.FormularioBoleto()
            if not self.json:
                self.json = cadastro.BOLETO_BASE
            carteiras = entidades.CarteiraParaBoleto().listar_ativas()
            self.carteiras = [{'id': carteira.id, 'nome': carteira.nome, 'numero': carteira.numero} for carteira in carteiras]
            self.bancos = [{'id': banco[0], 'nome': banco[1]} for banco in set([(carteira.banco_id, carteira.banco_nome) for carteira in carteiras])]
            self.banco_carteira = {}
            if 'dias_vencimento' not in self.json:
                self.json['dias_vencimento'] = 2
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
            self.json.get('empresa_beneficiario', None) is not None and
            self.json.get('empresa_cnpj', None) is not None and
            self.json.get('empresa_estado', None) is not None and
            self.json.get('empresa_endereco', None) is not None and
            self.json.get('empresa_cidade', None) is not None and
            self.json.get('banco', None) is not None and
            self.json.get('carteira', None) is not None and
            self.json.get('banco_agencia', None) is not None and
            self.json.get('banco_conta', None) is not None and
            self.json.get('banco_convenio', None) is not None and
            self.json.get('linha_1', None) is not None
        )
