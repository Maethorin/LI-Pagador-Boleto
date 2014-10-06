# -*- coding: utf-8 -*-
import json
import os

from pagador.configuracao.cadastro import CampoFormulario, FormularioBase, TipoDeCampo, CadastroBase, SelecaoBase, FormatoDeCampo, ValidadorBase
from pagador.configuracao.cliente import Script, TipoScript
from pagador.configuracao.models import Banco, BoletoCarteira


def caminho_do_arquivo_de_template(arquivo):
    diretorio = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(diretorio, "templates", arquivo)


class MeioPagamentoCadastro(CadastroBase):
    campos_boleto = Script(tipo=TipoScript.html, eh_template=True, nome="complemento", caminho_arquivo=caminho_do_arquivo_de_template("campos_boleto.html"))

    @property
    def alerta(self):
        script = Script(tipo=TipoScript.html, nome="alerta")
        script.adiciona_linha('<div class="alert alert-info" style="margin-top: 20px;">')
        script.adiciona_linha(u'    <h4><strong>ATENÇÃO:</strong> Antes de habilitar o pagamento via Boleto Bancário é necessário efetuar a liberação da carteira bancário junto ao seu gerente.</h4>')
        script.adiciona_linha('</div>')
        return script

    @property
    def descricao_para_lojista(self):
        script = Script(tipo=TipoScript.html, nome="descricao")
        script.adiciona_linha(u'<p>Preencha todos os dados para habilitar o boleto bancário</p>')
        return script

    @property
    def contexto(self):
        bancos = Banco.objects.prefetch_related('carteiras').all()
        carteiras = BoletoCarteira.objects.filter(ativo=True)
        carteira_choices = [{"id": x.id, "nome": x.nome} for x in carteiras]
        banco_choices = [{"id": x[0], "nome": x[1]} for x in set([(y.banco.id, y.banco.nome) for y in carteiras])]
        banco_carteira_json = {}
        for banco in bancos:
            carteiras = banco.carteiras.filter(ativo=True)
            if carteiras:
                banco_carteira_json[str(banco.id)] = {}
                for carteira in carteiras:
                    banco_carteira_json[str(banco.id)][str(carteira.id)] = {'nome': carteira.nome, 'convenio': carteira.convenio}
        return {'bancos': banco_choices, "carteiras": carteira_choices, "banco_carteira_json": banco_carteira_json}

    def to_dict(self):
        return {
            "contexto": self.contexto,
            "html": [
                self.alerta.to_dict(),
                self.descricao_para_lojista.to_dict(),
                self.campos_boleto.to_dict()
            ]
        }


class ValidarJson(ValidadorBase):
    def __init__(self, valor):
        super(ValidarJson, self).__init__(valor)
        self.erros = {}

    @property
    def mensagem(self):
        return self.erros

    @property
    def eh_valido(self):
        try:
            data = json.loads(self.valor)
        except ValueError:
            self.erros["json"] = "Os dados enviados não puderam ser reconhecidos."
            return False

        def so_numeros(s):
            return u''.join([x for x in s if x.isdigit()])

        for i in ['empresa_cnpj', 'banco_agencia', 'banco_conta', 'banco_convenio']:
            if data.get(i):
                valor = so_numeros(data[i])
                if i != 'empresa_cnpj' and not valor:
                    self.erros[i] = u"Informação inválida. Deve conter apenas digitos."
                if i == 'empresa_cnpj' and len(valor) < 14:
                    self.erros['empresa_cnpj'] = u"CNPJ da empresa inválido."

        if data.get('desconto_valor', None):
            try:
                valor = float(data['desconto_valor'])
                if valor > 100.0 or valor < 0.0:
                    self.erros['desconto_valor'] = u"Porcentagem inválida. Insira um valor entre 0% e 100%."
            except ValueError:
                self.erros['desconto_valor'] = u"Porcentagem inválida. Insira um valor entre 0% e 100%."
        bancos_limites = {"2": 5, "1": 7, "6": 8, "4": 6}
        if data.get('banco_conta') and data.get('banco') and bancos_limites.get(data['banco']):
            conta = data['banco_conta']
            tamanho_atual = len(conta)
            tamanho_necessario = bancos_limites[data['banco']]
            if tamanho_atual != tamanho_necessario:
                self.erros["banco_conta"] = "Certifique-se de que o valor tenha %s caracteres (ele possui %s)." % (tamanho_necessario, tamanho_atual)

        endereco = u'%s - %s / %s' % (data.get('empresa_endereco'), data.get('empresa_cidade'), data.get('empresa_estado'))
        if len(endereco) > 80:
            self.erros["empresa_endereco"] = "O endereço, cidade e estado juntos não podem passar de 80 caracteres, reduza ou abrevie o endereço."

        return not self.erros


class Formulario(FormularioBase):
    json = CampoFormulario("json", "", requerido=True, ordem=1, tipo=TipoDeCampo.oculto, formato=FormatoDeCampo.json, validador=ValidarJson)


class MeioPagamentoEnvio(object):
    @property
    def css(self):
        return Script(tipo=TipoScript.css, caminho_arquivo=caminho_do_arquivo_de_template("style.css"))

    @property
    def function_enviar(self):
        return Script(tipo=TipoScript.javascript, eh_template=True, caminho_arquivo=caminho_do_arquivo_de_template("javascript.js"))

    @property
    def mensagens(self):
        return Script(tipo=TipoScript.html, caminho_arquivo=caminho_do_arquivo_de_template("mensagens.html"), eh_template=True)

    def to_dict(self):
        return [
            self.css.to_dict(),
            self.function_enviar.to_dict(),
            self.mensagens.to_dict()
        ]


class MeioPagamentoSelecao(SelecaoBase):
    selecao = Script(tipo=TipoScript.html, nome="selecao", caminho_arquivo=caminho_do_arquivo_de_template("selecao.html"), eh_template=True)

    def to_dict(self):
        return [
            self.selecao.to_dict()
        ]
