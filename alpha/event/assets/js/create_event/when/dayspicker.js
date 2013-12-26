;(function($, window, document, undefined) {
    function DaysPicker(element, when){
        this.element = element;
        this.when = when;
        this.days = [];
        this.initDeck();
    }

    DaysPicker.prototype = {
        initDeck: function(){
            this.labels = dom("div", {"class": "dtp-labels"}, [
                dom("p", {"innerHTML": "Start Time"}),
                dom("p", {"innerHTML": "End Time"}),
                dom("p", {"innerHTML": "Auto fill"}),
            ]);

            this.daysContainer = dom("div", {"class": "days-container"});
            
            $(this.element).append(this.labels).append(this.daysContainer);
        },
        clear: function() {
            for(var i in this.days) if(this.days.hasOwnProperty(i)) {
                $(this.days[i].element).remove();
            }
            this.days = [];
        },
        addDay: function(day, month, year) {
            var index, previous, timePicker;
            
            index = _.map(this.days, function(day) {
                return day.options.day
            }).indexOf(day);

            if(index !== -1) {
                $(this.days.splice(index, 1)[0].element).remove();
                return;
            }
            previous = this.findPrevious(day);
            timesPicker = this.createTimesPicker(day, month, year);

            if(this.days.length === 0) {
                this.days = [];
                $(this.labels).removeClass("active");
                $(this.labels).parents(".month-container").removeClass("hidden-arrows");
            } else {
                $(this.labels).addClass("active");
                $(this.labels).parents(".month-container").addClass("hidden-arrows");
            }

            if(previous) {
                this.days.splice(
                    this.days.indexOf(previous) + 1, 0, timesPicker
                );
                $(previous.element).after(timesPicker.element);
            } else {
                this.days.splice(0, 0, timesPicker);
                $(this.daysContainer).prepend(timesPicker.element);
            }
        },
        findNextMonth: function(){
            return this.when.findNextMonth(this);
        },
        findFirst: function(){
            if(this.days.length > 0) {
                return this.days[0];
            } else {
                return false;
            }

        },
        findPrevious: function(day) {
            if(this.days.length) {
                var maxDay, tempDay;
                for(var di in this.days) if(this.days.hasOwnProperty(di)) {
                    tempDay = this.days[di];
                    if(tempDay.options.day < day) {
                        maxDay = tempDay;
                    } else {
                        return maxDay || false;
                    }
                }
                return maxDay;
            } else {
                return false;
            }
        },
        findNext: function(day) {
            if(this.days.length) {
                var minDay = false,
                    tempDay;
                for(var di in this.days) if(this.days.hasOwnProperty(di)) {
                    tempDay = this.days[di];
                    if(tempDay.options.day > day) {
                        minDay = tempDay;
                        return minDay
                    }
                }
                return minDay;
            } else {
                return false;
            }
        },
        createTimesPicker: function(day, month, year) {
            var element = dom("div", {"class": "my-time-picker"});

            return new TimesPicker(element, this, {
                day: day,
                month: month,
                year: year
            });            
        }
    };

    window.DaysPicker = DaysPicker;

})(jQuery, window, document);   