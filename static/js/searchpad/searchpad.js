;(function($, window, document, undefined) {

    'use strict';

    var SearchPadPage = function(){
        this.initJumpToDate();
        this.initEventActions();
        $("#searchTags").tagit({
            afterTagRemoved: function(e, ui){
                window.location = $(ui.tag).data("remove-url");
            }
        });
    };

    SearchPadPage.prototype = {
        initJumpToDate: function(){
            this.jumpToDate = new window.JumpToDate();
        },
        initEventActions: function(){
            this.eventActions = new window.EventActions($(".event-details-block"));
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