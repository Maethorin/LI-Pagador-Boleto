# -*- coding: utf-8 -*-
import datetime
from pagador.configuracao.models import Banco

from pagador.envio.requisicao import Enviar
from pagador.retorno.models import SituacaoPedido

from unicodedata import normalize

from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixa
from pyboleto.bank.itau import BoletoItau
from pyboleto.html import BoletoHTML
from pyboleto.pdf import BoletoPDF
import StringIO
from repositories.configuracao.models import BoletoCarteira


class TipoBoleto(object):
    html = "html"
    pdf = "pdf"
    linha_digitavel = "linha_digitavel"


class EnviarPedido(Enviar):
    def __init__(self, pedido, dados, configuracao_pagamento):
        super(EnviarPedido, self).__init__(pedido, dados, configuracao_pagamento)
        self.processa_resposta = True
        self.url = None
        self.grava_identificador = False

    def obter_situacao_do_pedido(self, status_requisicao):
        return SituacaoPedido.SITUACAO_AGUARDANDO_PAGTO

    @property
    def endereco_completo(self):
        complemento = self.pedido.endereco_pagamento.complemento and (" - %s" % self.pedido.endereco_pagamento.complemento) or ""
        return "{}, {}{} - {}, {} / {} - CEP: {}".format(
            self.pedido.endereco_pagamento.endereco, self.pedido.endereco_pagamento.numero, complemento, self.pedido.endereco_pagamento.bairro,
            self.pedido.endereco_pagamento.cidade, self.pedido.endereco_pagamento.estado, self.pedido.endereco_pagamento.cep)

    def processar_resposta(self, resposta):
        if self.pedido.pagamento.codigo != 'boleto':
            return {"content": "Não foi encontrada forma de pagamento usando boleto bancário para o pedido {} na conta {}".format(self.pedido.numero, self.pedido.conta_id), "status": 404, "reenviar": False}
        sacado = [self.pedido.endereco_entrega.nome, self.endereco_completo]
        boleto = {}
        resultado = self.emitir_boleto(
            self.pedido.data_criacao.date(),
            self.pedido.data_criacao.date(),
            self.pedido.data_criacao.date() + datetime.timedelta(days=5),
            self.pedido.valor_total,
            sacado, self.pedido.numero,
            tipo=self.dados["tipo_boleto"]
        )
        if self.dados["tipo_boleto"] == TipoBoleto.linha_digitavel:
            boleto = {"linha_digitavel": resultado}
        if self.dados["tipo_boleto"] == TipoBoleto.html:
            boleto = {"html": resultado}
        if self.dados["tipo_boleto"] == TipoBoleto.pdf:
            boleto = {"pdf": resultado}
        return {
            "content": {
                "boleto": boleto
            },
            "status": 200,
            "reenviar": False
        }

    def para_ascii(self, texto):
        """Remove qualquer acentuação e qualquer caractere estranho."""
        try:
            return normalize('NFKD', texto.decode('utf-8')).encode('ASCII', 'ignore')
        except UnicodeEncodeError:
            return normalize('NFKD', texto).encode('ASCII', 'ignore')

    def emitir_boleto(self, data_processamento, data_documento, data_vencimento, valor_documento, sacado, numero_documento, nosso_numero=None, tipo=TipoBoleto.html):
        """Emite um boleto com os dados passados.
        Caso pdf seja True, retorna uma tupla com a linha digitável e a
        instância do arquivo PDF.
        """
        if not self.configuracao_pagamento.json:
            return None
        dados = self.configuracao_pagamento.json
        banco = Banco.objects.get(pk=dados['banco'])
        convenio = int(dados.get('banco_convenio') or 0)
        boleto = None
        if banco.nome == u'Bradesco':
            boleto = BoletoBradesco()
        elif banco.nome == u'Banco Itaú':
            boleto = BoletoItau()
        elif banco.nome == u'Banco do Brasil':
            if 1 <= convenio <= 9999:
                boleto = BoletoBB(4, 2)
            elif 1000 <= convenio <= 999999:
                boleto = BoletoBB(6, 2)
            else:
                boleto = BoletoBB(7, 2)
        elif banco.nome == u'Caixa Econômica':
            boleto = BoletoCaixa()
        carteira = BoletoCarteira.objects.get(pk=dados['carteira'], ativo=True)
        if not boleto:
            return {"erro": "Boleto para {} ainda não implementado.".format(banco.nome)}

        boleto.carteira = carteira.numero.encode('utf-8')
        boleto.cedente = dados['empresa_beneficiario'].encode('utf-8')
        boleto.cedente_documento = dados['empresa_cnpj'].encode('utf-8')
        boleto.cedente_endereco = (u'%s - %s / %s' % (dados['empresa_endereco'], dados['empresa_cidade'], dados['empresa_estado'])).encode('utf-8')
        boleto.agencia_cedente = dados['banco_agencia'].encode('utf-8')
        boleto.conta_cedente = dados['banco_conta'].encode('utf-8')
        if convenio:
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
        boleto.sacado = [self.para_ascii(texto) or texto for texto in boleto.sacado]
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
            return f_pdf
        return None