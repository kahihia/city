;(function($, window, document, undefined) {

    'use strict';

    var EventDaysSwitcher = function(){
        $(".event-day-switch").on("click", function(){
            if($(this).hasClass("active")) return;

            var day = $(this).data("day");
            $(".event-day-switch.active").removeClass("active")
            $(".show-time-day.active").removeClass("active")
            $(".show-day-description.active").removeClass("active")

            $(".event-day-switch[data-day='"+day+"']").addClass("active");
            $(".show-time-day[data-day='"+day+"']").addClass("active");
            $(".show-day-description[data-day='"+day+"']").addClass("active");
        });

        if($(".event-day-switch").length>5){
            var slider = $('.bxslider').bxSlider({
                infiniteLoop: false,
                hideControlOnEnd: true,
                minSlides: 5,
                maxSlides: 5,
                slideWidth: 62,
                slideMargin: 0,
                pager: false
            });
            $(".event-day-switch").each(function(index){
                if($(this).hasClass("active")){
                    slider.goToSlide((index+1)/5);    
                }                
            });
            
        }        
    };

    EventDaysSwitcher.prototype = {
        
    };

    window.EventDaysSwitcher = EventDaysSwitcher;

})(jQuery, window, document);