;(function($, window, document, undefined) {
    'use strict';

    var startScrolling = 170,
        topMargin = 145, top, maxScrolling, advertisingHeight;


    var AdvertisingScrolling = function(){
        $(window).scroll(this.improvePosition.bind(this));

        setTimeout(function(){
            $(".rotation-right-container").css({
                "transition": "top 500ms",
                "-webkit-transition": "top 500ms",
            });
        }, 100);
    };

    AdvertisingScrolling.prototype = {
        improvePosition: function(){
            startScrolling = $(".primary-content .main-content").offset().top - 11;
            topMargin = $(".primary-content .main-content").offset().top - 36;
            maxScrolling = $(".content-wrapper").height() - $(".rotation-right-container").height() + 10;
            advertisingHeight = $(".rotation-right-container").height();

            top = Math.min(($(window).scrollTop() - topMargin + $(window).height() - advertisingHeight - 10), maxScrolling );

            if(advertisingHeight > $(window).height() && top>25){
                $(".rotation-right-container").css({
                    top: top + "px"
                });
            } else if(advertisingHeight <= $(window).height() && $(window).scrollTop() > startScrolling) {
                top = Math.min(($(window).scrollTop()-topMargin), maxScrolling);
                $(".rotation-right-container").css({
                    top: top + "px"
                });
            } else {
                $(".rotation-right-container").css({
                    top: "25px"
                });
            }
        }
    };

    window.AdvertisingScrolling = AdvertisingScrolling;

})(jQuery, window, document);