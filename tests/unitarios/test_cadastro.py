# -*- coding: utf-8 -*-
import unittest

from pagador_boleto import cadastro


BANCOS = {'341': '2', '237': '1', '104': '6', '001': '4', '033': '7', '399': '3'}


class FormularioBoleto(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(FormularioBoleto, self).__init__(*args, **kwargs)
        self.formulario = cadastro.FormularioBoleto()

    def test_deve_ter_bancos(self):
        self.formulario.boleto.nome.should.be.equal('json')
        self.formulario.boleto.ordem.should.be.equal(0)
        self.formulario.boleto.formato.should.be.equal(cadastro.cadastro.FormatoDeCampo.json)
        self.formulario.boleto.tipo.should.be.equal(cadastro.cadastro.TipoDeCampo.oculto)
        self.formulario.boleto.validador.should.be.equal(cadastro.BoletoValidador)

    def test_deve_ter_ativo(self):
        self.formulario.ativo.nome.should.be.equal('ativo')
        self.formulario.ativo.ordem.should.be.equal(1)
        self.formulario.ativo.label.should.be.equal('Pagamento ativo?')
        self.formulario.ativo.tipo.should.be.equal(cadastro.cadastro.TipoDeCampo.boleano)

    def test_deve_ter_valor_minimo_aceitado(self):
        self.formulario.valor_minimo_aceitado.nome.should.be.equal('valor_minimo_aceitado')
        self.formulario.valor_minimo_aceitado.ordem.should.be.equal(2)
        self.formulario.valor_minimo_aceitado.label.should.be.equal(u'Valor mínimo')
        self.formulario.valor_minimo_aceitado.tipo.should.be.equal(cadastro.cadastro.TipoDeCampo.decimal)

    def test_deve_ter_desconto(self):
        self.formulario.tem_desconto.nome.should.be.equal('desconto')
        self.formulario.tem_desconto.ordem.should.be.equal(3)
        self.formulario.tem_desconto.label.should.be.equal(u'Usar desconto?')
        self.formulario.tem_desconto.tipo.should.be.equal(cadastro.cadastro.TipoDeCampo.boleano)

    def test_deve_ter_desconto_valor(self):
        self.formulario.desconto_valor.nome.should.be.equal('desconto_valor')
        self.formulario.desconto_valor.ordem.should.be.equal(4)
        self.formulario.desconto_valor.label.should.be.equal(u'Desconto aplicado')
        self.formulario.desconto_valor.tipo.should.be.equal(cadastro.cadastro.TipoDeCampo.decimal)
        self.formulario.desconto_valor.validador.should.be.equal(cadastro.DescontoValidador)

    def test_deve_ter_aplicar_no_total(self):
        self.formulario.aplicar_no_total.nome.should.be.equal('aplicar_no_total')
        self.formulario.aplicar_no_total.ordem.should.be.equal(5)
        self.formulario.aplicar_no_total.label.should.be.equal(u'Aplicar no total?')
        self.formulario.aplicar_no_total.tipo.should.be.equal(cadastro.cadastro.TipoDeCampo.boleano)


class ValidadorBoleto(unittest.TestCase):
    def test_deve_adicionar_erro_se_nao_for_dicionario(self):
        validador = cadastro.BoletoValidador(valor='nao-eh-dict')
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.contain('dados_invalidos')
        validador.erros['dados_invalidos'].should.be.equal(u'Os dados do boleto devem ser em formato de dicionário')

    def test_deve_adicionar_erro_para_atributos_faltando(self):
        validador = cadastro.BoletoValidador(valor={'sem_atributos': 1})
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.contain('atributos')
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo empresa_beneficiario no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo empresa_cnpj no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo empresa_estado no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo empresa_endereco no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo empresa_cidade no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo banco no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo carteira no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo banco_agencia no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo banco_conta no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo banco_convenio no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo linha_1 no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo linha_2 no boleto {'sem_atributos': 1}")
        validador.erros['atributos'].should.contain(u"Não foi enviado o atributo linha_3 no boleto {'sem_atributos': 1}")

    def test_cnpj_soh_pode_ter_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': '1233d44',
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
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'empresa_cnpj': u'CPF/CNPJ inválido. Deve ter 14 digitos para CNPJ ou 11 para CPF'})

    def test_cnpj_deve_ter_14_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': '12345678901234',
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
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_cpf_deve_ter_11_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': '12345678901',
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
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_banco_agencia_deve_ter_somente_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': None,
            'carteira': None,
            'banco_agencia': '12w3',
            'banco_conta': None,
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_agencia': u'Informação inválida. Deve conter apenas digitos.'})

    def test_banco_conta_deve_ter_somente_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': None,
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '12w3',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Informação inválida. Deve conter apenas digitos.'})

    def test_banco_convenio_deve_ter_somente_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': None,
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '12w3',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_convenio': u'Informação inválida. Deve conter apenas digitos.'})

    def test_banco_convenio_banco_brasil_nao_pode_ter_qtd_invalida_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['001'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '123',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_convenio': u'Certifique-se de que o valor tenha 6, 7 ou 8 caracteres (ele possui 3).'})

    def test_banco_convenio_banco_brasil_pode_ter_6_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': '001',
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '123456',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_banco_convenio_banco_brasil_pode_ter_7_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': '001',
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '1234567',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_banco_convenio_banco_brasil_pode_ter_8_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': '001',
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '12345678',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_banco_convenio_santander_deve_ter_7_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': '033',
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '1234567',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_banco_convenio_hsbc_deve_ter_7_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': '399',
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '1234567',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty

    def test_banco_convenio_santander_nao_deve_ter_diferente_7_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['033'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '12345678',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_convenio': u'Certifique-se de que o valor tenha 7 caracteres (ele possui 8).'})

    def test_banco_convenio_hsbc_deve_ter_diferente_7_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['399'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': None,
            'banco_convenio': '123456',
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_convenio': u'Certifique-se de que o valor tenha 7 caracteres (ele possui 6).'})

    def test_banco_itau_deve_ter_conta_com_5_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['341'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '1234',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Certifique-se de que o valor tenha 5 caracteres (ele possui 4).'})

    def test_banco_bradesco_deve_ter_conta_com_7_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['237'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '12345678',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Certifique-se de que o valor tenha 7 caracteres (ele possui 8).'})

    def test_banco_caixa_deve_ter_conta_com_6_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['104'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '12345',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Certifique-se de que o valor tenha 6 caracteres (ele possui 5).'})

    def test_banco_brasil_deve_ter_conta_com_6_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['001'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '12345',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Certifique-se de que o valor tenha 6 caracteres (ele possui 5).'})

    def test_banco_santander_deve_ter_conta_com_8_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['033'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '123456789',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Certifique-se de que o valor tenha 8 caracteres (ele possui 9).'})

    def test_banco_hspc_deve_ter_conta_com_5_digitos(self):
        boleto = {
            'empresa_beneficiario': None,
            'empresa_cnpj': None,
            'empresa_estado': None,
            'empresa_endereco': None,
            'empresa_cidade': None,
            'banco': BANCOS['399'],
            'carteira': None,
            'banco_agencia': None,
            'banco_conta': '123456',
            'banco_convenio': None,
            'linha_1': None,
            'linha_2': None,
            'linha_3': None,
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal({'banco_conta': u'Certifique-se de que o valor tenha 5 caracteres (ele possui 6).'})

    def test_retorna_ok_com_tudo_preenchido(self):
        boleto = {
            'empresa_beneficiario': 'Nome Beneficiario',
            'empresa_cnpj': '12345678901',
            'empresa_estado': 'RJ',
            'empresa_endereco': 'Endereco',
            'empresa_cidade': 'Cidade',
            'banco': '341',
            'carteira': '18',
            'banco_agencia': '1234',
            'banco_conta': '12345',
            'banco_convenio': None,
            'linha_1': 'Linha 1',
            'linha_2': 'Linha 2',
            'linha_3': 'Linha 3',
        }
        validador = cadastro.BoletoValidador(valor=boleto)
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty


class ValidarDesconto(unittest.TestCase):
    def test_deve_validar_maior_que_100(self):
        validador = cadastro.DescontoValidador(valor='123.94')
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal(u'Porcentagem inválida. Insira um valor entre 0% e 100%.')

    def test_deve_validar_menor_que_0(self):
        validador = cadastro.DescontoValidador(valor='-0.5')
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal(u'Porcentagem inválida. Insira um valor entre 0% e 100%.')

    def test_deve_validar_none(self):
        validador = cadastro.DescontoValidador(valor=None)
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal(u'Porcentagem inválida. Insira um valor entre 0% e 100%.')

    def test_deve_validar_se_valor_gerar_value_error(self):
        validador = cadastro.DescontoValidador(valor='asdds')
        validador.eh_valido.should.be.equal(False)
        validador.erros.should.be.equal(u'Porcentagem inválida. Insira um valor entre 0% e 100%.')

    def test_deve_retornar_ok_se_valor_for_certo(self):
        validador = cadastro.DescontoValidador(valor='50.43444')
        validador.eh_valido.should.be.equal(True)
        validador.erros.should.be.empty
