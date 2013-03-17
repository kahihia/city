;(function($, window, document, undefined) {

    'use strict';

    var SearchPadPage = function(){
        this.initJumpToDate();
    };

    SearchPadPage.prototype = {
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
        window.searchPadPage = new SearchPadPage();
    });

})(jQuery, window, document);