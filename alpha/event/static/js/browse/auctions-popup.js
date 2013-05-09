;(function($, window, document, undefined) {
    'use strict';

    var AuctionPopup = function(element){
        var that=this, hoverConfig;

        this.element = $(element);
        this.popup = $(".auctions-wrapper", this.element);

        this.ticketsPopupTrigger = $(".tickets-popup-trigger", this.element);
        this.ticketsPopup = $(".tickets-popup", this.element);

        this.ticketsPopupTrigger.on("click", this.showTicketsPopup.bind(this));

        hoverConfig = {
            sensitivity: 3,
            interval: 200,
            over: function(e){
                that.openPopup();
            },
            timeout: 500,
            out: function(e){
                that.closePopup();
            }
        };

        this.element.hoverIntent(hoverConfig);
    };

    AuctionPopup.prototype = {
        openPopup: function(e){
            $(".auctions-wrapper").hide();
            this.popup.show();
            e && e.stopPropagation();
        },
        closePopup: function(e){
            this.popup.hide();
        },
        closeIfNotPopup: function(e){
            if($(e.target).hasClass("auctions-wrapper") || $(e.target).parents(".auctions-wrapper").length>0){
                
            } else {
                this.closePopup();
            }
        },
        showTicketsPopup: function(){
            $(this.ticketsPopup).dialog({
                title: "Tickets:",
                modal: true,
                buttons: [
                    {
                        text: "OK",
                        click: function() {
                            $( this ).dialog( "close" );
                        }
                    }
                ]
            });
            return false;
        }
    };

    $.fn.auction_popup = function () {
        this.each(function () {
            new AuctionPopup(this);
        });
    };

    window.AuctionPopup = AuctionPopup;

})(jQuery, window, document);