//{% load filters %}
var url = '';
var $counter = null;
var segundos = 5;
$(function() {
    var $boletoMensagem = $(".boleto-mensagem");

    function enviaPagamento() {
        $boletoMensagem.find(".msg-danger").hide();
        $boletoMensagem.find(".msg-success").hide();
        $boletoMensagem.find(".msg-warning").show();
        $boletoMensagem.removeClass("alert-message-success");
        $boletoMensagem.removeClass("alert-message-danger");
        $boletoMensagem.addClass("alert-message-warning");
        var url_pagar = '{% url_loja "checkout_pagador" pedido.numero pagamento.id %}?tipo_boleto=linha_digitavel';
        $.getJSON(url_pagar)
            .fail(function (data) {
                exibeMensagemErro(data.status, data.content);
            })
            .done(function (data) {
                console.log(data);
                if (data.sucesso) {
                    $("#aguarde").hide();
                    exibeMensagemSucesso(data.content.boleto)
                }
                else {
                    exibeMensagemErro(data.status, data.content);
                }
            });
    }

    function exibeMensagemErro(status, mensagem) {
        $boletoMensagem.find(".msg-warning").hide();
        $boletoMensagem.toggleClass("alert-message-warning alert-message-danger");
        var $errorMessage = $("#errorMessage");
        $errorMessage.text(status + ": " + mensagem);
        $boletoMensagem.find(".msg-danger").show();
    }

    function exibeMensagemSucesso(boleto) {
        $boletoMensagem.find(".msg-warning").hide();
        $boletoMensagem.toggleClass("alert-message-warning alert-message-success");
        var $success = $boletoMensagem.find(".msg-success");
        var $dadosBoleto = $success.find("#successMessage");
        $dadosBoleto.find("#linhaDigitavel").text(boleto.linha_digitavel);
        $dadosBoleto.show();
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
