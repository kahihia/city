;(function($, window, document, undefined) {
    'use strict';

    function BuyTickets(eventDetailsBlock){
        var that=this;
        this.eventElement = eventDetailsBlock;

        this.buyTicketsButton = $(".action-buy-tickets", this.eventElement);

        this.buyTicketsButton.on("click", this.showBuyTicketsPopup.bind(this));

        this.dialogContainer = $(".buy-tickets-popup", that.eventElement).dialog({
            dialogClass: "event-action-ui-dialog",
            resizable: false,
            width: 390,
            autoOpen: false
        });
    }

    BuyTickets.prototype = {
        showBuyTicketsPopup: function(){
            $(this.dialogContainer).dialog('open');
        }
    }

    window.BuyTickets = BuyTickets;

})(jQuery, window, document);    