;(function($, window, document, undefined) {
    'use strict';

    var startScrolling = 170,
        topMargin = 145;


    var AdvertisingScrolling = function(){
        $(window).scroll(this.improvePosition.bind(this));
        this.improvePosition();
    };

    AdvertisingScrolling.prototype = {
        improvePosition: function(){
            if ($(window).scrollTop() > startScrolling){
                var maxScrolling = $(".content-wrapper").height() - $(".advertising-right-container").height() + 10;
                $(".advertising-right-container").css({
                    top: Math.min(
                            ($(window).scrollTop()-topMargin),
                            maxScrolling
                        ) + "px"
                });
            } else {
                $(".advertising-right-container").css({
                    top: "auto"
                });
            }
        }
    };

    window.AdvertisingScrolling = AdvertisingScrolling;


})(jQuery, window, document);