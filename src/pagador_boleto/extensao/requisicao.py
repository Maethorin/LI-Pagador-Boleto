# -*- coding: utf-8 -*-

from pagador.envio.requisicao import Enviar
from pagador.retorno.models import SituacaoPedido


class EnviarPedido(Enviar):
    def __init__(self, pedido, dados, configuracao_pagamento):
        super(EnviarPedido, self).__init__(pedido, dados, configuracao_pagamento)
        self.processa_resposta = True
        self.url = None
        self.grava_identificador = False

    def obter_situacao_do_pedido(self, status_requisicao):
        return SituacaoPedido.SITUACAO_AGUARDANDO_PAGTO

    def processar_resposta(self, resposta):
        try:
            pagamento_venda = self.pedido.pedido_venda_pagamento_da_forma_de_pagamento(pagamento_id=7)[0]
        except IndexError:
            return {"content": "Não foi encontrada forma de pagamento usando depósito bancário para o pedido {} na conta {}".format(self.pedido.numero, self.pedido.conta_id), "status": 404, "reenviar": False}
        pagamento_banco = pagamento_venda.banco
        email_comprovante = self.configuracao_pagamento.email_comprovante
        if not email_comprovante:
            email_comprovante = self.pedido.conta.email_contato
        return {
            "content": {
                "nome": pagamento_banco.banco.nome,
                "codigo": pagamento_banco.banco.codigo,
                "imagem": pagamento_banco.banco.imagem,
                "agencia": pagamento_banco.agencia,
                "numero_conta": pagamento_banco.numero_conta,
                "poupanca": pagamento_banco.poupanca,
                "favorecido": pagamento_banco.favorecido,
                "cpf": pagamento_banco.cpf,
                "cnpj": pagamento_banco.cnpj,
                "email_comprovante": email_comprovante,
                "informacao_complementar": self.configuracao_pagamento.informacao_complementar,
            },
            "status": 200,
            "reenviar": False
        }
