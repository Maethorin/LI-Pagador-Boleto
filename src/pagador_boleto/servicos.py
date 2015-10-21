# -*- coding: utf-8 -*-

import StringIO

from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixaSIGCB
from pyboleto.bank.hsbc import BoletoHsbc
from pyboleto.bank.itau import BoletoItau
from pyboleto.bank.santander import BoletoSantander
from pyboleto.html import BoletoHTML
from pyboleto.pdf import BoletoPDF

from pagador import servicos
from pagador_boleto import entidades


class BoletoInvalido(Exception):
    pass


class EntregaPagamento(servicos.EntregaPagamento):
    def __init__(self, loja_id, plano_indice=1, dados=None):
        super(EntregaPagamento, self).__init__(loja_id, plano_indice, dados=dados)
        self.tem_malote = True

    def define_pedido_e_configuracao(self, pedido_numero):
        try:
            super(EntregaPagamento, self).define_pedido_e_configuracao(pedido_numero)
        except self.EnvioDePagamentoInvalido, ex:
            if pedido_numero != 'TESTE-BOLETO':
                raise ex

    def processa_dados_pagamento(self):
        banco = self.malote.banco_nome
        convenio = self.malote.banco_convenio
        boleto = None
        if banco == u'Bradesco':
            boleto = BoletoBradesco()
        elif banco == u'Banco Itaú':
            boleto = BoletoItau()
        elif banco == u'Banco do Brasil':
            boleto = BoletoBB(len(convenio), 2)
        elif banco == u'Caixa Econômica':
            boleto = BoletoCaixaSIGCB()
        elif banco == u'Santander':
            boleto = BoletoSantander()
        elif banco == u'HSBC':
            boleto = BoletoHsbc()
        if not boleto:
            raise BoletoInvalido(u'Boleto para {} ainda não implementado.'.format(banco))

        carteira = self.malote.carteira_numero
        boleto.carteira = carteira.encode('utf-8')
        boleto.cedente = self.malote.empresa_beneficiario.encode('utf-8')

        tamanho_documento = len(self.malote.empresa_cnpj)
        tipo_documento = 'CNPJ' if tamanho_documento == 14 else 'CPF'
        documento = self.formatador.formata_cpf_cnpj(self.malote.empresa_cnpj.encode('utf-8'))
        boleto.cedente_documento = documento
        documento = ' / {}: {}'.format(tipo_documento, documento)
        limite = 80 - len(documento)
        cidade_estado = u', {}-{}'.format(self.malote.empresa_cidade, self.malote.empresa_estado).encode('utf-8')
        limite -= len(cidade_estado)
        rua = self.malote.empresa_endereco.encode('utf-8')[:limite]
        endereco = '{}{}{}'.format(rua, cidade_estado, documento)

        boleto.cedente_endereco = endereco

        boleto.agencia_cedente = self.malote.banco_agencia.encode('utf-8')
        boleto.conta_cedente = self.malote.banco_conta.encode('utf-8')
        if convenio:
            if banco in [u'Santander', u'HSBC', u'Bradesco', u'Caixa Econômica']:
                boleto.conta_cedente = convenio.encode('utf-8')
            else:
                boleto.convenio = convenio

        boleto.data_vencimento = self.malote.data_vencimento
        boleto.data_documento = self.malote.data_documento
        boleto.data_processamento = self.malote.data_processamento
        boleto.instrucoes = [self.malote.linha_1, self.malote.linha_2, self.malote.linha_3]
        boleto.instrucoes = [instrucao and instrucao.encode('utf-8') or instrucao for instrucao in boleto.instrucoes]
        boleto.valor_documento = self.malote.valor_documento
        sacado = self.malote.sacado
        if not isinstance(sacado, list):
            sacado = [sacado]
        boleto.sacado = sacado
        boleto.sacado = [self.formatador.string_para_ascii(texto) or texto for texto in boleto.sacado]
        boleto.sacado_documento = str(self.formatador.formata_cpf_cnpj(self.malote.sacado_documento))
        boleto.numero_documento = str(self.malote.numero_documento)
        if self.malote.nosso_numero:
            boleto.nosso_numero = str(self.malote.nosso_numero)
        else:
            boleto.nosso_numero = str(self.malote.numero_documento)

        linha_digitavel = boleto.linha_digitavel
        if self.malote.formato == entidades.TipoBoleto.linha_digitavel:
            self.resultado = {'dados': linha_digitavel}
        elif self.malote.formato == entidades.TipoBoleto.html:
            f_html = StringIO.StringIO()
            boleto_html = BoletoHTML(f_html)
            boleto_html.drawBoleto(boleto)
            boleto_html.save()
            f_html.seek(0)
            self.resultado = {'dados': f_html.read()}
        elif self.malote.formato == entidades.TipoBoleto.pdf:
            f_pdf = StringIO.StringIO()
            boleto_pdf = BoletoPDF(f_pdf)
            boleto_pdf.drawBoleto(boleto)
            boleto_pdf.save()
            f_pdf.seek(0)
            self.resultado = {'dados': unicode(f_pdf.read(), 'ISO-8859-1'), 'pago': True}
