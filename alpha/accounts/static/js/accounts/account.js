;(function($, window, document, undefined) {
    'use strict';

    function AccountPage(){
        this.openedTab = window.sessionStorage.getItem("account-tab-opened");
        if(this.openedTab){
            this.openTab(this.openedTab);
        }

        window.onbeforeunload = this.saveOpenedTab.bind(this);

        $(".entry-info").auction_popup();
    }

    AccountPage.prototype = {
        openTab: function(tabId){
            $(".tabs-container .tabs li[data-tab-id="+tabId+"]").click();
        },
        saveOpenedTab: function(){
            window.sessionStorage.setItem("account-tab-opened", $(".tabs-container .tabs li.current").data("tab-id"));
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
        }
    };

    $(document).on("ready page:load", function(){
        window.accountPage = new AccountPage();
    });

})(jQuery, window, document);