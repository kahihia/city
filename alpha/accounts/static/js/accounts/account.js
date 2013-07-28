;(function($, window, document, undefined) {
    'use strict';

    function AccountPage(){
        this.advertising_stats = new AdvertisingStats();
    }

    AccountPage.prototype = {
                
    };

    $(document).on("ready page:load", function(){
        window.accountPage = new AccountPage();
    });

})(jQuery, window, document);