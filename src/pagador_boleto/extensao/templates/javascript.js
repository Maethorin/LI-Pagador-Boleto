//{% load filters %}
var url = '';
var $counter = null;
var segundos = 5;
$(function() {
    var $depositoMensagem = $(".deposito-mensagem");

    function enviaPagamento() {
        $depositoMensagem.find(".msg-danger").hide();
        $depositoMensagem.find(".msg-success").hide();
        $depositoMensagem.find(".msg-warning").show();
        $depositoMensagem.removeClass("alert-message-success");
        $depositoMensagem.removeClass("alert-message-danger");
        $depositoMensagem.addClass("alert-message-warning");
        var url_pagar = '{% url_loja "checkout_pagador" pedido.numero pagamento.id %}';
        $.getJSON(url_pagar)
            .fail(function (data) {
                exibeMensagemErro(data.status, data.content);
            })
            .done(function (data) {
                console.log(data);
                if (data.sucesso) {
                    $("#aguarde").hide();
                    exibeMensagemSucesso(data.content)
                }
                else {
                    exibeMensagemErro(data.status, data.content);
                }
            });
    }

    function exibeMensagemErro(status, mensagem) {
        $depositoMensagem.find(".msg-warning").hide();
        $depositoMensagem.toggleClass("alert-message-warning alert-message-danger");
        var $errorMessage = $("#errorMessage");
        $errorMessage.text(status + ": " + mensagem);
        $depositoMensagem.find(".msg-danger").show();
    }

    function exibeMensagemSucesso(banco) {
        $depositoMensagem.find(".msg-warning").hide();
        $depositoMensagem.toggleClass("alert-message-warning alert-message-success");
        var $success = $depositoMensagem.find(".msg-success");
        var $dadosBanco = $success.find("#successMessage");
        var url_imagem = '{{ ADMIN_STATIC_URL }}img/formas-de-pagamento/' + banco.imagem;
        $dadosBanco.find("#bancoImagem").attr("src", url_imagem);
        $dadosBanco.find("#bancoNome").text(banco.nome);
        $dadosBanco.find("#bancoCodigo").text(banco.codigo);
        $dadosBanco.find("#bancoAgencia").text(banco.agencia);
        $dadosBanco.find("#bancoConta").text(banco.numero_conta);
        $dadosBanco.find("#bancoPoupanca").hide();
        if (banco.poupanca) {
            $dadosBanco.find("#bancoPoupanca").show();
        }
        if (banco.cpf) {
            $dadosBanco.find("#bancoNomeDocumento").text("CPF:");
            $dadosBanco.find("#bancoCpfCnpj").text(banco.cpf);
        }
        else if (banco.cnpj) {
            $dadosBanco.find("#bancoNomeDocumento").text("CNPJ:");
            $dadosBanco.find("#bancoCpfCnpj").text(banco.cnpj);
        }
        else {
            $dadosBanco.find("#documentoNome").hide();
            $dadosBanco.find("#bancoCpfCnpj").hide();
        }
        $dadosBanco.find("#bancoFavorecido").text(banco.favorecido);
        $dadosBanco.find("#bancoEmailComprovante").text(banco.email_comprovante);
        $dadosBanco.find("#bancoInformacoesComplementares").text(banco.informacao_complementar);
        $dadosBanco.show();
        $success.show();
    }

    $(".msg-danger").on("click", ".pagar", function() {
        enviaPagamento();
    });

    var pedidoPago = '{{ pedido.situacao_id }}' == '4';

    if (pedidoPago) {
        exibeMensagemSucesso("pago");
    }
    else {
        enviaPagamento();
    }
});
