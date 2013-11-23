;(function($, window, document, undefined) {

    'use strict';

    var EventDaysSwitcher = function(){
        var that = this;

        this.viewer = $(".events-occurrences");
        this.content = $(".event-days", this.viewer);
        this.next = $(".next", this.viewer);
        this.prev = $(".prev", this.viewer);
        this.days = $("li", this.content).length;

        this.currentDay = +$(".event-day-switch.active").data("counter");

        this.prev.on("click", this.scrollPrevPage.bind(this));
        this.next.on("click", this.scrollNextPage.bind(this));

        $(".event-day-switch").on("click", function(){
            if($(this).hasClass("active")) return;

            var day = $(this).data("day");
            $(".event-day-switch.active").removeClass("active")
            $(".show-time-day.active").removeClass("active")
            $(".show-day-description.active").removeClass("active")

            $(".event-day-switch[data-day='"+day+"']").addClass("active");
            $(".show-time-day[data-day='"+day+"']").addClass("active");
            $(".show-day-description[data-day='"+day+"']").addClass("active");

            that.currentDay = +$(".event-day-switch.active").data("counter");
            that.scrollToActiveDay();
        });

        this.scrollToActiveDay();
    };

    EventDaysSwitcher.prototype = {
        _scroll: function(){
            var leftPosition = -97*(this.currentDay-2);
            if(this.currentDay==1) {
                leftPosition -= 97;
            }
            if(this.currentDay==this.days) {
                leftPosition += 97;
            }
            $(this.content).animate({                
                "left": leftPosition + "px"
            });
        },
        scrollToDay: function(day){
            if(day>0 && day<=this.days){
                this.currentDay = day;
                this._scroll();
            }
        },
        scrollNextPage: function(){
            this.scrollToDay(this.currentDay+1);
        },
        scrollPrevPage: function(){
            this.scrollToDay(this.currentDay-1);
        },
        scrollToActiveDay: function(){
            this.scrollToDay(this.currentDay);
        }
    };

    window.EventDaysSwitcher = EventDaysSwitcher;

})(jQuery, window, document);