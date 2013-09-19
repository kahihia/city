;(function($, window, document, undefined) {

    'use strict';

    var EventDaysSwitcher = function(){
        $(".event-day-switch").on("click", function(){
            if($(this).hasClass("active")) return;

            var day = $(this).data("day");
            $(".event-day-switch.active").removeClass("active")
            $(".show-time-day.active").removeClass("active")

            $(".event-day-switch[data-day='"+day+"']").addClass("active");
            $(".show-time-day[data-day='"+day+"']").addClass("active");
        });
    };

    EventDaysSwitcher.prototype = {
        
    };

    window.EventDaysSwitcher = EventDaysSwitcher;

})(jQuery, window, document);