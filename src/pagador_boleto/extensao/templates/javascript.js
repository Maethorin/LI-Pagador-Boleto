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
        var url_pagar = '{% url_loja "checkout_pagador" pedido.numero pagamento.id %}?formato=linha_digitavel';
        $.getJSON(url_pagar)
            .fail(function (data) {
                exibeMensagemErro(data.status, data.content);
            })
            .done(function (data) {
                if (data.sucesso) {
                    $("#aguarde").hide();
                    exibeMensagemSucesso(data.content)
                }
                else if (data.status == 404) {
                    var fatal = false;
                    if (data.content.hasOwnProperty("fatal")) {
                        fatal = data.content.fatal;
                    }
                    exibeMensagemErro(data.status, data.content.mensagem, fatal);
                }
                else {
                    if ('{{ settings.DEBUG }}' == 'True') {
                        exibeMensagemErro(data.status, data.content);
                    }
                    else {
                        exibeMensagemErro(data.status, "Ocorreu um erro ao enviar sua solicitação. Se o erro persistir, contate nosso SAC.");
                    }
                }
            });
    }

    function exibeMensagemErro(status, mensagem, fatal) {
        $boletoMensagem.find(".msg-warning").hide();
        $boletoMensagem.toggleClass("alert-message-warning alert-message-danger");
        var $errorMessage = $("#errorMessage");
        $errorMessage.text(status + ": " + mensagem);
        $boletoMensagem.find(".msg-danger").show();
        if (fatal) {
            $(".pagar").remove();
            $(".click").remove();
        }
    }

    function exibeMensagemSucesso(linha_digitavel) {
        $boletoMensagem.find(".msg-warning").hide();
        $boletoMensagem.toggleClass("alert-message-warning alert-message-success");
        var $success = $boletoMensagem.find(".msg-success");
        var $dadosBoleto = $success.find("#successMessage");
        $dadosBoleto.find("#linhaDigitavel").text(linha_digitavel);
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
