# -*- coding: utf-8 -*-
import json

from pagador.reloaded import entidades
from pagador_boleto.reloaded import cadastro


class ConfiguracaoMeioPagamento(entidades.ConfiguracaoMeioPagamento):
    _campos = ['ativo', 'valor_minimo_aceitado', 'desconto_valor', 'aplicar_no_total', 'json']
    _codigo_gateway = 8

    def __init__(self, loja_id, codigo_pagamento=None):
        super(ConfiguracaoMeioPagamento, self).__init__(loja_id, codigo_pagamento)
        self.preencher_do_gateway(self._codigo_gateway, self._campos)
        self.formulario = cadastro.FormularioBoleto()
        if not self.json:
            self.json = cadastro.BOLETO_BASE
        carteiras = entidades.CarteiraParaBoleto().listar_ativas()
        self.carteiras = [{"id": carteira.id, "nome": carteira.nome} for carteira in carteiras]
        self.bancos = [{"id": banco[0], "nome": banco[1]} for banco in set([(carteira.banco_id, carteira.banco_nome) for carteira in carteiras])]
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
