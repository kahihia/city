;(function($, window, document, undefined) {
    'use strict';

    var BrowsePage = function(){
        this.initJumpToDate();
        $(".entry-info").auction_popup();
    };

    BrowsePage.prototype = {
        initJumpToDate: function(){
            this.jumpToDate = new window.JumpToDate();
        },
        showTicketsPopup: function(){
            $(".tickets-popup").dialog({
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

    $(window).load(function(){
        window.browsePage = new BrowsePage();
    });

})(jQuery, window, document);