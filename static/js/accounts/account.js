;(function($, window, document, undefined) {
    'use strict';

    function AccountPage(){
        this.openedTab = window.sessionStorage.getItem("account-tab-opened");
        if(this.openedTab){
            this.openTab(this.openedTab);
        }

        window.onbeforeunload = this.saveOpenedTab.bind(this);
    }

    AccountPage.prototype = {
        openTab: function(tabId){
            $(".tabs-container .tabs li[data-tab-id="+tabId+"]").click();
        },
        saveOpenedTab: function(){
            window.sessionStorage.setItem("account-tab-opened", $(".tabs-container .tabs li.current").data("tab-id"));
        }
    };

    $(document).on("ready page:load", function(){
        window.accountPage = new AccountPage();
    });

})(jQuery, window, document);