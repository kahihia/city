;(function($, window, document, undefined) {
    'use strict';

    function AdvertisingPaymentPage(){
        $("a.advertising-image").fancybox({
            'transitionIn'  :   'elastic',
            'transitionOut' :   'elastic',
            'speedIn'       :   600, 
            'speedOut'      :   200, 
            'overlayShow'   :   false
        });
    }

    AdvertisingPaymentPage.prototype = {       
        
    };

    $(document).on("ready page:load", function(){
        window.advertisingPaymentPage = new AdvertisingPaymentPage();        
    });

})(jQuery, window, document);