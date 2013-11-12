;(function($, window, document, undefined) {
    'use strict';

    var BrowsePage = function(){
        this.initJumpToDate();
        $(".browse.searchtags").tagit({
            afterTagRemoved: function(e, ui){
                window.location = $(ui.tag).data("remove-url");
            }
        });

        this.initEventActions();
        //this.initMoreLessButtons(); commented because of buttons logic changing
    };

    BrowsePage.prototype = {
        initJumpToDate: function(){
            this.jumpToDate = new window.JumpToDate(
                $(".primary-content")
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
                $(".all-tags-container").addClass('more');
            });

            $(".less-button").on("click", function(){
                $(".all-tags-container").removeClass('more');
            });
        }
    };

    $(document).on("ready page:load", function(){
        window.browsePage = new BrowsePage();
    });

})(jQuery, window, document);