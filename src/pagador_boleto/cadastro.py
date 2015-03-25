# -*- coding: utf-8 -*-

from li_common.padroes import cadastro


BOLETO_BASE = {
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


class BoletoValidador(cadastro.ValidadorBase):

    @property
    def eh_valido(self):
        if type(self.valor) is not dict:
            self.erros['dados_invalidos'] = u'Os dados do boleto devem ser em formato de dicionário'
            return False

        erros = []
        for chave in BOLETO_BASE:
            if chave not in self.valor:
                erros.append(u'Não foi enviado o atributo {} no boleto {}'.format(chave, self.valor))
        if erros:
            self.erros['atributos'] = erros
            return False

        def so_numeros(numeros):
            return u''.join([algaritimo for algaritimo in numeros if algaritimo.isdigit()])

        dados_boleto = self.valor
        banco = dados_boleto['banco']
        for campo in ['empresa_cnpj', 'banco_agencia', 'banco_conta', 'banco_convenio']:
            if dados_boleto.get(campo):
                valor = so_numeros(dados_boleto[campo])
                if campo != 'empresa_cnpj' and valor != dados_boleto[campo]:
                    self.erros[campo] = u'Informação inválida. Deve conter apenas digitos.'
                if campo == 'empresa_cnpj' and (len(valor) != 14 and len(valor) != 11):
                    self.erros['empresa_cnpj'] = u'CPF/CNPJ inválido. Deve ter 14 digitos para CNPJ ou 11 para CPF'
                if campo == 'banco_convenio':
                    tamanho_atual = len(dados_boleto[campo])
                    if banco == '4' and tamanho_atual not in [6, 7, 8]:
                        self.erros[campo] = u'Certifique-se de que o valor tenha 6, 7 ou 8 caracteres (ele possui {}).'.format(tamanho_atual)
                    if banco in ['3', '7'] and not tamanho_atual == 7:
                        self.erros[campo] = u'Certifique-se de que o valor tenha 7 caracteres (ele possui {}).'.format(tamanho_atual)
        bancos_limites = {'2': 5, '1': 7, '6': 6, '4': 6, '7': 8, '3': 5}
        if dados_boleto.get('banco_conta') and banco and bancos_limites.get(banco):
            conta = dados_boleto['banco_conta']
            tamanho_atual = len(conta)
            tamanho_necessario = bancos_limites[dados_boleto['banco']]
            if tamanho_atual != tamanho_necessario:
                self.erros['banco_conta'] = u'Certifique-se de que o valor tenha {} caracteres (ele possui {}).'.format(tamanho_necessario, tamanho_atual)

        return not self.erros


class DescontoValidador(cadastro.ValidadorBase):
    @property
    def eh_valido(self):
        try:
            valor = float(self.valor)
            if valor > 100.0 or valor < 0.0:
                self.erros = u'Porcentagem inválida. Insira um valor entre 0% e 100%.'
        except (TypeError, ValueError):
            self.erros = u'Porcentagem inválida. Insira um valor entre 0% e 100%.'
        return not self.erros


class FormularioBoleto(cadastro.Formulario):
    boleto = cadastro.CampoFormulario('json', ordem=0, tipo=cadastro.TipoDeCampo.oculto, formato=cadastro.FormatoDeCampo.json, validador=BoletoValidador)

    ativo = cadastro.CampoFormulario('ativo', 'Pagamento ativo?', tipo=cadastro.TipoDeCampo.boleano, ordem=1)
    valor_minimo_aceitado = cadastro.CampoFormulario('valor_minimo_aceitado', u'Valor mínimo', requerido=False, decimais=2, ordem=2, tipo=cadastro.TipoDeCampo.decimal, texto_ajuda=u'Informe o valor mínimo para exibir esta forma de pagamento.')
    tem_desconto = cadastro.CampoFormulario('desconto', u'Usar desconto?', requerido=False, ordem=3, tipo=cadastro.TipoDeCampo.boleano, texto_ajuda=u'Define se o depósito usará desconto.')
    desconto_valor = cadastro.CampoFormulario('desconto_valor', u'Desconto aplicado', requerido=False, ordem=4, decimais=2, tipo=cadastro.TipoDeCampo.decimal, validador=DescontoValidador)
    aplicar_no_total = cadastro.CampoFormulario('aplicar_no_total', u'Aplicar no total?', requerido=False, ordem=5, tipo=cadastro.TipoDeCampo.boleano, texto_ajuda=u'Aplicar desconto no total da compra (incluir por exemplo o frete).')
