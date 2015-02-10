# -*- coding: utf-8 -*-
import datetime
import StringIO

from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixaSIGCB
from pyboleto.bank.hsbc import BoletoHsbc
from pyboleto.bank.itau import BoletoItau
from pyboleto.bank.santander import BoletoSantander
from pyboleto.html import BoletoHTML
from pyboleto.pdf import BoletoPDF
from repositories.configuracao.models import BoletoCarteira

from pagador.configuracao.models import Banco, PagamentoNaoConfigurado
from pagador.envio.requisicao import Enviar


class TipoBoleto(object):
    html = "html"
    pdf = "pdf"
    linha_digitavel = "linha_digitavel"

    @classmethod
    def eh_valido(cls, formato):
        return formato in [prop for prop in dir(cls) if not prop.startswith("__")]


class EnviarPedido(Enviar):
    def __init__(self, pedido, dados, configuracao_pagamento):
        super(EnviarPedido, self).__init__(pedido, dados, configuracao_pagamento)
        self.processa_resposta = True
        self.url = None
        self.deve_gravar_dados_de_pagamento = False

    def obter_situacao_do_pedido(self, status_requisicao):
        return None

    @property
    def endereco_completo(self):
        complemento = self.pedido.endereco_pagamento.complemento and (" - %s" % self.pedido.endereco_pagamento.complemento) or ""
        return u"{}, {}{} - {}, {} / {} - CEP: {}".format(
            self.pedido.endereco_pagamento.endereco, self.pedido.endereco_pagamento.numero, complemento, self.pedido.endereco_pagamento.bairro,
            self.pedido.endereco_pagamento.cidade, self.pedido.endereco_pagamento.estado, self.pedido.endereco_pagamento.cep)

    def processar_resposta(self, resposta):
        if self.pedido.pagamento.codigo != 'boleto':
            return {"content": u"Não foi encontrada forma de pagamento usando boleto bancário para o pedido {} na conta {}".format(self.pedido.numero, self.pedido.conta_id), "status": 404, "reenviar": False}
        sacado = [self.pedido.endereco_entrega.nome, self.endereco_completo]
        formato = TipoBoleto.linha_digitavel
        if "formato" in self.dados:
            formato = self.dados["formato"]
        if not TipoBoleto.eh_valido(formato):
            formato = TipoBoleto.linha_digitavel

        conteudo = self.emitir_boleto(
            self.pedido.data_criacao.date(),
            self.pedido.data_criacao.date(),
            self.pedido.data_criacao.date() + datetime.timedelta(days=5),
            self.pedido.valor_total,
            sacado,
            self.pedido.numero,
            tipo=formato
        )
        return {
            "content": conteudo,
            "status": 200,
            "reenviar": False
        }

    def emitir_boleto(self, data_processamento, data_documento, data_vencimento, valor_documento, sacado, numero_documento, nosso_numero=None, tipo=TipoBoleto.html):
        if not self.configuracao_pagamento.json:
            raise PagamentoNaoConfigurado(u"Os dados do boleto não foram salvos no painel da loja.")
        dados = self.configuracao_pagamento.json
        banco = Banco.objects.get(pk=dados['banco'])
        convenio = dados.get('banco_convenio')
        boleto = None
        if banco.nome == u'Bradesco':
            boleto = BoletoBradesco()
        elif banco.nome == u'Banco Itaú':
            boleto = BoletoItau()
        elif banco.nome == u'Banco do Brasil':
            boleto = BoletoBB(len(convenio), 2)
        elif banco.nome == u'Caixa Econômica':
            boleto = BoletoCaixaSIGCB()
        elif banco.nome == u'Santander':
            boleto = BoletoSantander()
        elif banco.nome == u'HSBC':
            boleto = BoletoHsbc()
        carteira = BoletoCarteira.objects.get(pk=dados['carteira'], ativo=True)
        if not boleto:
            return {"erro": u"Boleto para {} ainda não implementado.".format(banco.nome)}

        boleto.carteira = carteira.numero.encode('utf-8')
        boleto.cedente = dados['empresa_beneficiario'].encode('utf-8')

        tamanho_documento = len(dados['empresa_cnpj'])
        tipo_documento = "CNPJ" if tamanho_documento == 14 else "CPF"
        documento = self.formatador.formata_cpf_cnpj(dados['empresa_cnpj'].encode('utf-8'))
        boleto.cedente_documento = documento
        documento = " / {}: {}".format(tipo_documento, documento)
        limite = 80 - len(documento)
        cidade_estado = u', {}-{}'.format(dados['empresa_cidade'], dados['empresa_estado']).encode('utf-8')
        limite -= len(cidade_estado)
        rua = dados['empresa_endereco'].encode('utf-8')[:limite]
        endereco = '{}{}{}'.format(rua, cidade_estado, documento)

        boleto.cedente_endereco = endereco

        boleto.agencia_cedente = dados['banco_agencia'].encode('utf-8')
        boleto.conta_cedente = dados['banco_conta'].encode('utf-8')
        if convenio:
            if banco.nome in [u'Santander', u'HSBC']:
                boleto.conta_cedente = convenio.encode('utf-8')
            else:
                boleto.convenio = convenio

        boleto.data_vencimento = data_vencimento
        boleto.data_documento = data_documento
        boleto.data_processamento = data_processamento
        boleto.instrucoes = [dados['linha_1'], dados['linha_2'], dados['linha_3']]
        boleto.instrucoes = [instrucao and instrucao.encode('utf-8') or instrucao for instrucao in boleto.instrucoes]
        boleto.valor_documento = valor_documento
        if not isinstance(sacado, list):
            sacado = [sacado]
        boleto.sacado = sacado
        boleto.sacado = [self.formatador.string_para_ascii(texto) or texto for texto in boleto.sacado]
        boleto.numero_documento = str(numero_documento)
        if nosso_numero:
            boleto.nosso_numero = str(nosso_numero)
        else:
            boleto.nosso_numero = str(numero_documento)

        linha_digitavel = boleto.linha_digitavel
        if tipo == TipoBoleto.linha_digitavel:
            return linha_digitavel
        elif tipo == TipoBoleto.html:
            f_html = StringIO.StringIO()
            boleto_html = BoletoHTML(f_html)
            boleto_html.drawBoleto(boleto)
            boleto_html.save()
            f_html.seek(0)
            return f_html.read()
        elif tipo == TipoBoleto.pdf:
            f_pdf = StringIO.StringIO()
            boleto_pdf = BoletoPDF(f_pdf)
            boleto_pdf.drawBoleto(boleto)
            boleto_pdf.save()
            f_pdf.seek(0)
            return unicode(f_pdf.read(), "ISO-8859-1")
        return None
