;(function($, window, document, undefined) {
    'use strict';

    function AdvertisingFundPage(){
        this.initTotalPriceCalculation();
        this.initSwitchPaymemtModes();
    }

    AdvertisingFundPage.prototype = {        
        initTotalPriceCalculation: function(){
            this.totalPriceCalculation = new TotalPriceCalculation();
        },
        initSwitchPaymemtModes: function(){

        }
    };


    $(document).on("ready page:load", function(){
        var ballons;
        window.advertisingSetupPage = new AdvertisingFundPage();
        $.balloon.defaults.classname = "hintbox";
        $.balloon.defaults.css = {};
        ballons = $(".balloon");
        $(ballons).each(function(){
            var content = $(this).siblings(".balloon-content");
            $(this).balloon({
                contents:content,
                position:"left bottom",
                tipSize: 0,
                offsetX:0,//$.browser.msie?0:25,
                offsetY:25,//$.browser.msie?25:0,
                showDuration: 500, hideDuration: 0,
                showAnimation: function(d) { this.fadeIn(d); }
            });
        });
    });

})(jQuery, window, document);