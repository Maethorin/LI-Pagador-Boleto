# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
import mock
from pagador_boleto.reloaded import servicos, entidades


class BoletoEntregandoPagamento(unittest.TestCase):
    def setUp(self):
        dados_json = {
            'empresa_beneficiario': 'Beneficiario', 'empresa_cnpj': '12345678901', 'empresa_estado': 'RJ', 'empresa_endereco': u'Endereço Empresa', 'empresa_cidade': 'Rio de Janeiro',
            'banco': '1',
            'carteira': '1',
            'banco_agencia': '1234', 'banco_conta': '23445', 'banco_convenio': None,
            'linha_1': 'LINHA 1',
            'linha_2': '',
            'linha_3': '',
        }
        nomes_bancos = [u'Bradesco', u'Banco Itaú', u'Banco do Brasil', u'Caixa Econômica', u'Santander', u'HSBC', u'Não Existe']
        numeros_carteiras = ['25', '175', '18', 'SR', '102', 'CNR', 'NE']
        carteiras = [{'id': i + 1, 'nome': 'Carteira {}'.format(numeros_carteiras[i]), 'numero': numeros_carteiras[i]} for i in range(0, len(numeros_carteiras))]
        bancos = [{'id': i + 1, 'nome': nomes_bancos[i]} for i in range(0, len(nomes_bancos))]
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

    def test_entrega_tem_malote(self):
        entrega = servicos.EntregaPagamento(234)
        entrega.tem_malote.should.be.truthy

    def test_processa_dados_pagamento_bradesco(self):
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '23791.23421 50000.000120 34002.344504 1 63580000010040'})

    def test_envia_passando_sacado_sem_ser_lista(self):
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        self.malote.sacado = 'Um Sacado'
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '23791.23421 50000.000120 34002.344504 1 63580000010040'})

    def test_processa_dados_pagamento_bradesco_com_nosso_numero(self):
        self.malote.nosso_numero = 12344
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '23791.23421 50000.001235 44002.344503 3 63580000010040'})

    def test_processa_dados_pagamento_itau(self):
        self.malote.configuracao.json['banco'] = '2'
        self.malote.configuracao.json['carteira'] = '2'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '34191.75009 00123.431231 42344.560000 8 63580000010040'})

    def test_processa_dados_pagamento_banco_brasil_convenio_6(self):
        self.malote.configuracao.json['banco'] = '3'
        self.malote.configuracao.json['carteira'] = '3'
        self.malote.configuracao.json['banco_convenio'] = '123456'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '00191.23454 60000.000004 00001.234210 5 63580000010040'})

    def test_processa_dados_pagamento_banco_brasil_convenio_7(self):
        self.malote.configuracao.json['banco'] = '3'
        self.malote.configuracao.json['carteira'] = '3'
        self.malote.configuracao.json['banco_convenio'] = '1234567'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '00190.00009 01234.567004 00001.234186 5 63580000010040'})

    def test_processa_dados_pagamento_banco_brasil_convenio_8(self):
        self.malote.configuracao.json['banco'] = '3'
        self.malote.configuracao.json['carteira'] = '3'
        self.malote.configuracao.json['banco_convenio'] = '12345678'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '00190.00009 01234.567806 00001.234186 9 63580000010040'})

    def test_processa_dados_pagamento_caixa_economica(self):
        self.malote.configuracao.json['banco'] = '4'
        self.malote.configuracao.json['carteira'] = '4'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '10490.23441 51000.200041 00000.123455 2 63580000010040'})

    def test_processa_dados_pagamento_santander(self):
        self.malote.configuracao.json['banco'] = '5'
        self.malote.configuracao.json['carteira'] = '5'
        self.malote.configuracao.json['banco_convenio'] = '1234567'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '03399.12347 56700.000005 01234.301024 3 63580000010040'})

    def test_processa_dados_pagamento_hsbc(self):
        self.malote.configuracao.json['banco'] = '6'
        self.malote.configuracao.json['carteira'] = '6'
        self.malote.configuracao.json['banco_convenio'] = '1234567'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '39991.23452 67000.000009 01234.064523 8 63580000010040'})

    def test_dar_erro_para_banco_nao_existente(self):
        self.malote.configuracao.json['banco'] = '7'
        self.malote.configuracao.json['carteira'] = '7'
        self.malote.monta_conteudo(self.pedido, {}, dados={})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento.when.called_with().should.throw(servicos.BoletoInvalido, u'Boleto para Não Existe ainda não implementado.')

    def test_boleto_em_html(self):
        self.malote.configuracao.json['banco'] = '2'
        self.malote.configuracao.json['carteira'] = '2'
        self.malote.monta_conteudo(self.pedido, {}, dados={'formato': 'html'})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': '<!DOCTYPE html>\n  <html lang="en">\n    <head>\n      <title>Boleto banc\xc3\xa1rio</title>\n      <meta charset="utf-8" />\n      <style>\n        html,body {margin:0;padding:0}\n        hr {border:1px dashed #000}\n        p {margin:0}\n        table {table-layout:fixed}\n        table td {overflow:hidden;white-space: nowrap}\n        .pagina {width:750px;font-family:Helvetica, Arial, "Lucida Grande", sans-serif;font-size:12px;margin:40px auto;}\n        .recibo-sacado {margin-bottom:50px}\n        .demonstrativo {height:190px}\n        .demonstrativo-content,.instrucoes-content {padding:3px}\n        .autenticacao-mecanica {height:80px}\n        .recibo-caixa {margin-top:30px}\n        .cabecalho td {border-bottom:4px solid #000;vertical-align:bottom;padding:0}\n        .cabecalho td.banco-logo {width:170px}\n        .cabecalho td.banco-logo img {float:left;margin:0;padding:0}\n        .cabecalho td.banco-codigo {width:70px;font-size:22px;font-weight:700;text-align:center}\n        .cabecalho td.bol-linha-digitavel {border-right:none;text-align:right;font-size:16px;font-weight:700}\n        .cabecalho .linhas-v {border-left:3px solid #000;border-right:3px solid #000}\n        .corpo td {border-bottom:1px solid #000;border-right:1px solid #000;vertical-align:top;height:27px;padding:0 2px}\n        .corpo td.linha-vazia {border-bottom:none}\n        .recibo-sacado .corpo tr td:last-child {border-right:none;text-align:left}\n        .recibo-caixa .corpo tr td:last-child {border-right:none;text-align:right;width:140px}\n        .rodape td {border:none;vertical-align:top;padding-left:2px}\n        .rodape td.bol-codigo-barras {padding:8px 6px}\n        .rotulo {text-align:left;font-size:9px;margin-bottom:2px}\n        .autenticacao-mecanica .rotulo {text-align:right}\n        tr.linha-grossa td, td.linha-grossa {border-bottom:3px solid #000}\n        .recibo-sacado .corpo .col-cedente-agencia,.recibo-sacado .corpo .col-cedente-documento {width:140px}\n        .recibo-sacado .corpo .col-vencimento {width:100px}\n        .recibo-caixa .corpo .col-data-documento {width:120px}\n        .recibo-caixa .corpo .col-numero-documento {width:140px}\n        .recibo-caixa .rodape .col-sacado {width:40px}\n        .recibo-caixa .rodape .col-codigo-baixa {width:210px}\n        .cabecalho,.corpo,.rodape {width:100%;border-collapse:collapse}\n        .recibo-caixa .corpo .col-especie-documento,.recibo-caixa .corpo .col-aceite {width:70px}\n        .bol-codigo-barras {height:40px}\n        #barcode {height: 60px}\n        #barcode span {margin: 0;padding-bottom: 34px;height: 16px}\n        .n {border-left: 1px solid}\n        .w {border-left: 3px solid}\n        .n, .w {border-color: #000}\n        .s {border-color: #fff}\n        /* @media print{ .pagina {page-break-after:always} } */\n      </style>\n    </head>\n    <body>\n      <div class="pagina">\n<div class="recibo-sacado">\n  <table class="cabecalho">\n    <tbody>\n      <tr>\n        <td class="banco-logo">\n          <img src="data:image/jpeg;base64,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" alt="Logo do banco" />\n        </td>\n        <td class="banco-codigo">\n          <div class="linhas-v">341-7</div>\n        </td>\n        <td class="bol-linha-digitavel">Recibo do Pagador</td>\n      </tr>\n    </tbody>\n  </table>\n  <table class="corpo">\n    <tbody>\n      <tr>\n        <td>\n          <div class="rotulo">Benefici\xc3\xa1rio</div>\n          Beneficiario\n        </td>\n        <td class="col-cedente-agencia">\n          <div class="rotulo">Ag\xc3\xaancia/C\xc3\xb3digo do Benefici\xc3\xa1rio</div>\n          1234/23445-6\n        </td>\n        <td class="col-cedente-documento">\n          <div class="rotulo">CPF/CNPJ do Benefici\xc3\xa1rio</div> 123.456.789-01\n        </td>\n        <td class="col-vencimento">\n          <div class="rotulo">Vencimento</div> 05/03/2015\n        </td>\n      </tr>\n      <tr>\n        <td>\n          <div class="rotulo">Pagador</div> Cliente entrega\n        </td>\n        <td>\n          <div class="rotulo">Nosso N\xc3\xbamero</div> 175/00001234-3\n        </td>\n        <td>\n          <div class="rotulo">N. do documento</div> 1234\n        </td>\n        <td>\n          <div class="rotulo">Data Documento</div> 28/02/2015\n        </td>\n      </tr>\n      <tr>\n        <td colspan="3">\n          <div class="rotulo">Endere\xc3\xa7o do Benefici\xc3\xa1rio</div> Endere\xc3\xa7o Empresa, Rio de Janeiro-RJ / CPF: 123.456.789-01\n        </td>\n        <td width="100px" class="col-dir">\n          <div class="rotulo">Valor Documento</div> 100,40\n        </td>\n      </tr>\n    </tbody>\n  </table>\n</div>\n<div class="demonstrativo">\n  <div class="rotulo">Demonstrativo</div>\n  <div class="demonstrativo-content"></div>\n</div>\n<div class="autenticacao-mecanica">\n  <div class="rotulo">Autentica\xc3\xa7\xc3\xa3o Mec\xc3\xa2nica</div>\n</div>\n<hr /><div class="recibo-caixa">\n  <table class="cabecalho">\n    <tbody>\n      <tr>\n        <td class="banco-logo">\n          <img src="data:image/jpeg;base64,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" alt="Logo do banco" />\n        </td>\n        <td class="banco-codigo">\n          <div class="linhas-v">341-7</div>\n        </td>\n        <td class="bol-linha-digitavel">34191.75009 00123.431231 42344.560000 8 63580000010040</td>\n      </tr>\n    </tbody>\n  </table>\n  <table class="corpo">\n    <tbody>\n      <tr>\n        <td colspan="6">\n          <div class="rotulo">Local de pagamento</div> At\xc3\xa9 o vencimento, preferencialmente no Ita\xc3\xba.\n        </td>\n        <td>\n          <div class="rotulo">Vencimento</div> 05/03/2015\n        </td>\n      </tr>\n      <tr>\n        <td colspan="6">\n          <div class="rotulo">Benefici\xc3\xa1rio</div> Beneficiario\n        </td>\n        <td>\n          <div class="rotulo">Ag\xc3\xaancia / C\xc3\xb3d. do Benefici\xc3\xa1rio</div>\n          1234/23445-6\n        </td>\n      </tr>\n      <tr>\n        <td class="col-data-documento">\n          <div class="rotulo">Data do documento</div> 28/02/2015\n        </td>\n        <td class="col-numero-documento" colspan="2">\n          <div class="rotulo">N. do documento</div> 1234\n        </td>\n        <td class="col-especie-documento">\n          <div class="rotulo">Esp\xc3\xa9cie doc</div> DM\n        </td>\n        <td class="col-aceite">\n          <div class="rotulo">Aceite</div> N\n        </td>\n        <td>\n          <div class="rotulo">Data processamento</div> 28/02/2015\n        </td>\n        <td>\n          <div class="rotulo">Nosso n\xc3\xbamero</div> 175/00001234-3\n        </td>\n      </tr>\n      <tr>\n        <td>\n          <div class="rotulo">Uso do banco</div>\n        </td>\n        <td>\n          <div class="rotulo">Carteira</div> 175\n        </td>\n        <td>\n          <div class="rotulo">Esp\xc3\xa9cie</div> R$\n        </td>\n        <td colspan="2">\n          <div class="rotulo">Quantidade</div> \n        </td>\n        <td>\n          <div class="rotulo">Valor</div> \n        </td>\n        <td>\n          <div class="rotulo">(=) Valor documento</div> 100,40\n        </td>\n      </tr>\n      <tr>\n        <td colspan="6" rowspan="5" class="linha-grossa">\n          <div class="rotulo">Instru\xc3\xa7\xc3\xb5es\n          (Todas as informa\xc3\xa7\xc3\xb5es deste bloqueto s\xc3\xa3o de exclusiva\n           responsabilidade do benefici\xc3\xa1rio)</div>\n           <div class="instrucoes-content"><p>LINHA 1</p><p></p><p></p></div>\n        </td>\n        <td>\n          <div class="rotulo">(-) Descontos / Abatimentos</div>\n        </td>\n      </tr>\n      <tr>\n        <td>\n          <div class="rotulo">(-) Outras dedu\xc3\xa7\xc3\xb5es</div>\n        </td>\n      </tr>\n      <tr>\n        <td>\n          <div class="rotulo">(+) Mora/Multa</div>\n        </td>\n      </tr>\n      <tr>\n        <td>\n          <div class="rotulo">(+) Outros acr\xc3\xa9scimos</div>\n        </td>\n      </tr>\n      <tr>\n        <td class="linha-grossa">\n          <div class="rotulo">(=) Valor cobrado</div>\n        </td>\n      </tr>\n    </tbody>\n  </table>\n  <table class="rodape">\n    <tbody>\n      <tr class="linha-grossa">\n        <td class="col-sacado"><div class="rotulo">Pagador</div></td>\n        <td colspan="3"><p>Cliente entrega</p><p>Endereco, 23, complemento - Bairro, Cidade / MG - CEP: 33555666</p></td>\n      </tr>\n      <tr>\n      <td colspan="3" class="bol-codigo-barras">\n         <div id="barcode"><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="w s"></span><span class="w"></span><span class="w s"></span><span class="n"></span><span class="n s"></span><span class="w"></span><span class="n s"></span><span class="n"></span></div>\n      </td>\n      <td>\n        <div class="rotulo">Autentica\xc3\xa7\xc3\xa3o Mec\xc3\xa2nica / Ficha de Compensa\xc3\xa7\xc3\xa3o</div>\n      </td>\n      </tr>\n    </tbody>\n  </table>\n</div>\n<hr /></div></body></html>'})

    @mock.patch('pagador_boleto.reloaded.servicos.StringIO.StringIO')
    @mock.patch('pagador_boleto.reloaded.servicos.BoletoPDF')
    def test_boleto_em_pdf(self, boleto_pdf_mock, string_mock):
        f_pdf_mock = mock.MagicMock()
        f_pdf_mock.read.return_value = 'BOLETO_PDF'
        string_mock.return_value = f_pdf_mock
        self.malote.configuracao.json['banco'] = '2'
        self.malote.configuracao.json['carteira'] = '2'
        self.malote.monta_conteudo(self.pedido, {}, dados={'formato': 'pdf'})
        entrega = servicos.EntregaPagamento(234)
        entrega.malote = self.malote
        entrega.processa_dados_pagamento()
        entrega.resultado.should.be.equal({'dados': 'BOLETO_PDF'})
