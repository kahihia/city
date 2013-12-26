;(function($, window, document, undefined) {
    function MultiDayEvent(whenWidget){
        this.whenWidget = whenWidget;
        this.element = dom("div", {"class": "multiple-day-event"}, [
            dom("span", {"innerHTML": "Multiple Day Event"}),
            this.checkbox = dom("div", {"class": "checkbox white"}),
            this.popup = dom("div", {"class": "multiple-day-event-popup", "innerHTML": "By selecting this option your days will be grouped as one event and displayed like this: <br> Fri, Sept 24 - Sun, Sept 15<br><br>Leave blank if you want your days listed as single day events:<br>Friday, Sept 13"})
        ]);

        $(this.element).on("mouseover", this.showPopup.bind(this));
        $(this.element).on("mouseout", this.hidePopup.bind(this));

        $(this.checkbox).on("click", function(){
            $(this).toggleClass("checked");
        });

        this.load();
        setInterval(this.refreshWidget.bind(this), 100);
    }

    MultiDayEvent.prototype = {
        load: function(){
            if($("#id_event_type").val()=="MULTIDAY") {
                $(this.checkbox).addClass("checked");
            }
        },
        getElement: function(){
            return this.element;
        },
        show: function(){
            $(this.element).show();
        },
        hide: function(){
            $(this.element).hide();
            $(this.checkbox).removeClass("checked");
        },
        showPopup: function(){
            $(this.popup).show();
        },
        hidePopup: function(){
            $(this.popup).hide();
        },
        refreshWidget: function(){
            if(this.checkIfMultiDayEventPosible()){
                this.show();
            } else {
                this.hide();
            }
        },
        checkIfMultiDayEventPosible: function(){
            var days = this.whenWidget.getDays(),
                oneDay = 24*60*60*1000;

            if(days.length<2) return false;

            firstDay = days[0];
            lastDay = days[days.length-1];

            return (days.length-1) == Math.round((lastDay.getTime() - firstDay.getTime())/oneDay);
        },
        is_turned_on: function(){
            if(this.checkIfMultiDayEventPosible() && $(this.checkbox).hasClass("checked")) {                
                return true;
            } else {
                return false;
            }
        }
    }

    window.MultiDayEvent = MultiDayEvent;

})(jQuery, window, document);