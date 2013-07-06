;(function($, window, document, undefined) {
    'use strict';

    var BrowsePage = function(){
        this.initJumpToDate();
        $(".entry-info").auction_popup();
        $("#searchTags").tagit({
            afterTagRemoved: function(e, ui){
                window.location = $(ui.tag).data("remove-url");
            }
        });

        this.initEventActions();

        this.initMoreLessButtons();
    };

    BrowsePage.prototype = {
        initJumpToDate: function(){
            this.jumpToDate = new window.JumpToDate(
                $(".main-content")
            );
        },
        initEventActions: function(){
            $(".entry-info").each(function(){
                new window.EventActions($(this));
            });
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
        },
        initMoreLessButtons: function(){
            $(".more-button").on("click", function(){
                $(".main-navigation-nav-wrapper").addClass('more');
            });

            $(".less-button").on("click", function(){
                $(".main-navigation-nav-wrapper").removeClass('more');
            });
        }
    };

    $(document).on("ready page:load", function(){
        window.browsePage = new BrowsePage();
    });

})(jQuery, window, document);