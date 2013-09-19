(function($) {
    // For IE8 and earlier version.
    if(!Date.now) {
        Date.now = function() {
            return new Date().valueOf();
        }
    }
    if(!Array.prototype.indexOf) {
        Array.prototype.indexOf = function(obj, start) {
            for(var i = (start || 0), j = this.length; i < j; i++) {
                if(this[i] === obj) {
                    return i;
                }
            }
            return -1;
        }
    }

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

        if($("#id_when_multidayevent").val()=="true") {
            $(this.checbox).addClass("checked");
        }

        setInterval(this.refreshWidget.bind(this), 100);
    }

    MultiDayEvent.prototype = {
        getElement: function(){
            return this.element;
        },
        show: function(){
            $(this.element).show();
        },
        hide: function(){
            $(this.element).hide();
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
            if($("#id_when_multitimeevent").val()=="true"){
                return false;
            }

            var days = this.whenWidget.getDays(),
                oneDay = 24*60*60*1000;

            if(days.length<2) return false;

            firstDay = days[0];
            lastDay = days[days.length-1];

            return (days.length-1) == (lastDay.getTime() - firstDay.getTime())/oneDay;
        },
        is_turned_on: function(){
            if(this.checkIfMultiDayEventPosible() && $(this.checkbox).hasClass("checked")) {                
                return true;
            } else {
                return false;
            }
        }
    }

    function MultiTimeEvent(whenWidget){
        var that=this;
        this.whenWidget = whenWidget;

        this.times = [];

        this.addMoreTimeButton = dom("div", {"class": "add-new-time-button", "innerHTML": "+"});
        setTimeout(function(){
            $(whenWidget.deck).on("click", ".add-new-time-button", that.addMoreTime.bind(that));        
        }, 10);        

        setInterval(this.refreshWidget.bind(this), 100);
    }

    MultiTimeEvent.prototype = {
        show: function(){
            var dayWidget = $(".days-container .my-time-picker").data("ui-myTimepicker");
            $(dayWidget.label).append(this.addMoreTimeButton);
            $(this.addMoreTimeButton).show();

            this.dayWidget = dayWidget;
        },
        hide: function(){
            if(this.addMoreTimeButton.parentNode) {
                this.addMoreTimeButton.parentNode.removeChild(this.addMoreTimeButton);    
            }

            this.clear();
        },
        refreshWidget: function(){
            if(this.checkIfMultiTimeEventPosible()) {
                if(!this.visible){
                    this.show();
                }
                
                this.visible = true;
            } else {
                if(this.visible){
                    this.hide();
                }
                this.visible = false;
            }
        },
        checkIfMultiTimeEventPosible: function(){
            if($("#id_when_multidayevent").val()=="true"){
                return false;
            }
            return this.whenWidget.getDays().length==1;
        },
        is_turned_on: function(){
            if(this.checkIfMultiTimeEventPosible() && this.times.length>0) {
                return true;
            } else {
                return false;
            }
        },
        addMoreTime: function(){
            var eventTimesWidget = new EventTimesWidget(this);
            this.times.push(eventTimesWidget);

            $(".days-container .my-time-picker").after(eventTimesWidget.element);
        },
        removeEventTimesWidget: function(widget){
            var index = this.times.indexOf(widget);
            if(widget.element.parentNode) {
                widget.element.parentNode.removeChild(widget.element);    
            }

            if(index!==-1){
                this.times.splice(index, 1);
            }
        },
        clear: function(){
            while(this.times.length){
                this.removeEventTimesWidget(this.times[0]);
            }
        },
        getOccurrencesJSON: function(){
            var dayWidget = $(".days-container .my-time-picker").data("ui-myTimepicker");

            return JSON.stringify(
                _.map([dayWidget].concat(this.times), function(dayTimePicker){
                    return dayTimePicker.getValue();
                })
            );
        },
        validate: function(){
            for(var i in this.times) if(this.times.hasOwnProperty(i)) {
                var day = this.times[i].getValue();
                if(!day.startTime || !day.endTime) return false;
            }
            return true;
        }
    }

    function EventTimesWidget(parent){
        var that = this;
        this.parent = parent;
        this.element = dom("div", {"class": "my-additional-time-picker"}, [
            this.startTime = dom("input", {"class": "start-time"}),
            this.endTime = dom("input", {"class": "end-time"}),        
            this.removeButton = dom("div", {"class": "remove"})
        ]);        
            
        timepickerOptions = {
            minutes: {
                interval: 15
            },
            hours: {
                starts: 0,
                ends: 11
            },
            rows: 2,
            showPeriod: true,
            defaultTime: '1:00 PM'
        }

        $(this.startTime).timepicker(timepickerOptions);
        $(this.endTime).timepicker(timepickerOptions);

        $(this.removeButton).on('click', function() {
            if(confirm("Do you realy want to remove time?")) {
                that.parent.removeEventTimesWidget(that);
            }
        });
    }

    EventTimesWidget.prototype = {
        getValue: function() {
            return {
                startTime: $(this.startTime).val(),
                endTime: $(this.endTime).val()
            }
        },
        setValue: function(value) {
            $(this.startTime).val(value.startTime);
            $(this.endTime).val(value.endTime);
        }
    }


    $.widget("ui.when", {
        _create: function() {
            this.months = {
                //  2012: { 10: }
            };
            this._initDeck();
        },
        _initDeck: function() {
            var that = this,
                date = new Date(),
                disabledOrEnableMonths;

            this.multiDayEvent = new MultiDayEvent(this);
            this.multiTimeEvent = new MultiTimeEvent(this);

            this.deck = dom("div", {"class": "ui-widget when-deck"}, [
                this.error = dom("div", {"class": "error", "innerHTML": "Please choose the start/end time for the days you've selected"}),
                this.multiSelectMode = dom("span", {"innerHTML": "Use Shift Key to select more than one day"}),
                this.monthsContainer = dom("div", {"class": "months-container"}),
                this.monthPicker = dom("div", {"class": "month-picker"}),
                this.multiDayEvent.getElement(),
                this.resetButton = dom("div", {"class": "reset-button", "innerHTML": "Clear"}),
                this.cancelButton = dom("div", {"class": "cancel-button", "innerHTML": "Cancel"}),
                this.submitButton = dom("div", {"class": "submit-button", "innerHTML": "Submit"})
            ]);

            $(this.element).after(this.deck);

            $(this.monthPicker).newMonthPicker();

            $(this.monthPicker).on("monthselected", function(event, year, month) {
                that.addMonth(year, month);
            });

            disabledOrEnableMonths = function(year) {
                //TODO: disable month in used
                if((year || date.getFullYear()) == (new Date()).getFullYear()) {
                    var allMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        disabledMonths;
                    disabledMonths = _.filter(allMonths, function(month) {
                        return month < (new Date().getMonth() + 1);
                    });
                    $($(that.monthPicker).data("ui-newMonthPicker").monthValue).monthpicker('disableMonths', disabledMonths);

                } else {
                    $($(that.monthPicker).data("ui-newMonthPicker").monthValue).monthpicker('disableMonths', []);
                }
            };

            setTimeout(disabledOrEnableMonths, 100);

            $($(this.monthPicker).data("ui-newMonthPicker").monthValue).monthpicker().bind("monthpicker-change-year", function(e, year) {
                disabledOrEnableMonths(year);
            });

            this.addMonth(date.getFullYear(), date.getMonth() + 1);

            $(this.element).on("click focus", function() {
                setTimeout(function() {
                    $.fancybox($(that.deck), {
                        autoSize: true,
                        closeBtn: true,
                        hideOnOverlayClick: false
                    });
                }, 100);
            });

            $(this.resetButton).on("click", function() {
                var agree = confirm("Are you sure you want to clear form?")
                if(agree) {
                    that.clear(true);
                }
            });

            $(this.cancelButton).on("click", function() {
                $.fancybox.close();
                $(that.error).hide();
            });

            $(this.submitButton).on("click", function() {
                var valid = that.validate();
                if(valid) {
                    $.fancybox.close();
                    $(that.error).hide();
                    $(that.element).val(that.getText());
                    $("#id_description").data("ui-description").setDays(that.getDays());
                    that.refreshEventType();
                } else {
                    $(that.error).show();
                }
            });            
        },
        setValue: function(years) {
            for(yi in years) if(years.hasOwnProperty(yi)) {
                var months = years[yi];
                for(mi in months) if(months.hasOwnProperty(mi)) {
                    var days = months[mi];
                    this.addMonth(yi, mi);
                    for(di in days) if(days.hasOwnProperty(di)) {
                        var start = days[di].start,
                            end = days[di].end,
                            daysTimePicker = this.months[yi][mi],
                            format_day, timePicker;

                        daysTimePicker.addDay(parseInt(di), parseInt(mi), parseInt(yi));

                        format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(yi, mi - 1, di));
                        $(".days-picker", $(daysTimePicker.element).parents(".months-container")).multiDatesPicker('addDates', format_day);

                        timePicker = _.filter(daysTimePicker.days, function(day) {
                            return day.options.day == di;
                        })[0];
                        $(timePicker.startTime).val(start);
                        $(timePicker.endTime).val(end);
                    }
                }
            }
            $(this.element).val(this.getText());
        },
        addMonth: function(year, month) {
            var monthContainer, days, date, prevDaysTimePicker;

            if((year in this.months) && (month in this.months[year])) {
                return;
            }
            
            date = new Date();
            date.setDate(1);
            year && date.setFullYear(year);
            month && date.setMonth(month - 1);
            
            prevDaysTimePicker = this.findPrevDaysTimePicker(year, month);
            monthContainer = this.monthContainer(date, year, month);

            if(prevDaysTimePicker) {
                $(prevDaysTimePicker).after(monthContainer);
            } else {
                $(this.monthsContainer).prepend(monthContainer);
            }

            days = $(".days-time-picker", monthContainer).data("ui-daystimepicker");

            if(!(year in this.months)){
                this.months[year] = {};  
            }
            this.months[year][month] = days;
        },
        removeMonth: function(year, month) {
            delete this.months[year][month];
            if(this.months[year].length == 0) {
                delete this.months[year];
            }
        },
        findPrevDaysTimePicker: function(year, month) {
            var element;
            $(".month-container .days-picker").each(function() {
                if((year > this.year) || ((year == this.year) && (month > this.month))) {
                    element = $(this).parents(".month-container")[0];
                }
            });
            return element;
        },
        monthContainer: function(date, year, month) {
            var that = this,
                widget, daysTimePicker, multiSelectModeWrapper, removeButton, daysPicker, monthAndDaysWrapper, yesterday = (new Date());
            yesterday = yesterday.setDate(yesterday.getDate() - 1);

            monthAndDaysWrapper = dom("div", {"class": "month-and-days-wrapper"}, [
                multiSelectModeWrapper = dom("div", {"class": "multi-select-mode-wrapper"}, [
                    removeButton = dom("span", {"class": "remove"})
                ]),
                daysPicker = dom("div", {"class": "days-picker"})
            ]);            

            $(daysPicker).multiDatesPicker({
                onToggle: function(dateText) {
                    var timepicker = $(daysTimePicker).data("ui-daystimepicker"),
                        dateArray = dateText.split("/"),
                        month = parseInt(dateArray[0]),
                        day = parseInt(dateArray[1]),
                        year = parseInt(dateArray[2]);

                    timepicker.addDay(day, month, year);

                    if(timepicker.days.length === 0) {
                        $(timepicker.labels).removeClass("active");
                        $(timepicker.labels).parents(".month-container").removeClass("hidden-arrows");
                    } else {
                        $(timepicker.labels).addClass("active");
                        $(timepicker.labels).parents(".month-container").addClass("hidden-arrows");
                    }
                },
                onChangeMonthYear: function(year, month) {
                    that.removeMonth(this.year, this.month);
                    if((year in that.months) && (month in that.months[year])) {
                        year = this.year;
                        month = this.month;
                    }
                    $(this).parents(".month-container").remove();
                    that.addMonth(year, month);
                },
                beforeShowDay: function(date) {
                    return [date >= yesterday];
                },
                mode: 'normal',
                defaultDate: date
            });

            daysPicker.year = year;
            daysPicker.month = month;            

            $(removeButton).on("click", function() {
                if($(".month-container").length === 1) {
                    alert("You can not remove this month");
                    return;
                }
                if(confirm("Do you realy want to remove this month?")) {
                    that.removeMonth(daysPicker.year, daysPicker.month);
                    $(this).parents(".month-container").remove();
                }
            })            

            daysTimePicker = dom("div", {"class": "days-time-picker"});
            $(daysTimePicker).daystimepicker();

            return dom("div", {"class": "month-container"}, [monthAndDaysWrapper, daysTimePicker]);
        },
        getText: function() {
            var days = this.getDays(),
                minDay, maxDay;
            if(days.length === 0) return '';
            
            minDay = Math.min.apply(null, days);
            maxDay = Math.max.apply(null, days);
            if(minDay === maxDay) {
                return $.datepicker.formatDate('dd-M-yy', new Date(minDay));
            } else {
                return $.datepicker.formatDate('dd-M-yy', new Date(minDay)) + ' to ' + $.datepicker.formatDate('dd-M-yy', new Date(maxDay));
            }

        },
        getJson: function() {
            var value = {};
            for(var yi in this.months) if(this.months.hasOwnProperty(yi)) {
                var months = this.months[yi];
                value[yi] = {};
                for(var mi in months) if(months.hasOwnProperty(mi)) {
                    var days = months[mi].days;
                    value[yi][mi] = {}
                    for(var di in days) if(days.hasOwnProperty(di)) {
                        var times = days[di];
                        value[yi][mi][times.options.day] = {
                            start: $(times.startTime).val(),
                            end: $(times.endTime).val(),
                        }
                    }
                }
            }

            $("#id_when_json").val(JSON.stringify(value));
            return value;
        },
        getDays: function() {
            var json = this.getJson(),
                result = [];
            for(var year in json) if(json.hasOwnProperty(year)) {
                months = json[year];
                for(var month in months) if(months.hasOwnProperty(month)) {
                    days = months[month];
                    for(var day in days) if(days.hasOwnProperty(day)) {
                        result.push(new Date(year, month - 1, day));
                    }
                }
            }
            return result;
        },
        validate: function() {
            var json = this.getJson(),
                valid = true;
            for(var year in json) if(json.hasOwnProperty(year)) {
                months = json[year];
                for(var month in months) if(months.hasOwnProperty(month)) {
                    days = months[month];
                    for(var day in days) if(days.hasOwnProperty(day)) {
                        if(!days[day].start || !days[day].end) return false;
                    }
                }
            }

            if(!this.multiTimeEvent.validate()){
                return false;
            }
            return true;
        },
        clear: function(open) {
            $(this.deck).remove();
            this.months = {};
            this._initDeck();
            if(open) {
                $.fancybox($(this.deck), {
                    autoSize: true,
                    closeBtn: true,
                    hideOnOverlayClick: false
                });
            }
        },
        refreshEventType: function(){
            var mode="SINGLE";
            if(this.multiDayEvent.is_turned_on()){
                mode = "MULTIDAY";
            } else if(this.multiTimeEvent.is_turned_on()) {
                mode = "MULTITIME";

                $("#id_occurrences_json").val(this.multiTimeEvent.getOccurrencesJSON());
            }
            $("#id_event_type").val(mode)
        }

    });

    $.widget("ui.newMonthPicker", {
        _create: function() {
            var that = this,
                date;
            date = new Date();
            id = "mp_" + (+Date.now());

            this.monthValue = dom("input", {"class": "hidden monthpicker", "data-month-id": id});
            this.selectWrapper = dom("div", {"class": "wrapper"}, [
                this.label = dom("span", {"innerHTML": "Select More Months"}),
                this.selectButton = dom("div", {"class": "new-month-select-arrow"})
            ]);

            $(this.element).append(this.monthValue).append(this.selectWrapper);

            if(date.getMonth() == 11) {
                date.setFullYear(date.getFullYear() + 1)
                date.setMonth(0);
            } else {
                date.setMonth(date.getMonth() + 1)
            }

            $(this.monthValue).monthpicker({
                openOnFocus: false,
                id: id,
                startYear: date.getFullYear(),
                finalYear: date.getFullYear() + 5
            });

            $(this.selectWrapper).on("click", function() {
                $(that.monthValue).monthpicker('show');
            });

            $(this.monthValue).monthpicker().bind('monthpicker-click-month', function(e, month) {
                var monthpicker = $(this).data("monthpicker"),
                    year;
                year = monthpicker.settings.selectedYear;
                // bug in monthpicker
                if(monthpicker.settings.startYear > monthpicker.settings.selectedYear) {
                    year = monthpicker.settings.startYear
                }
                $(that.element).trigger("monthselected", [year, month]);
            });
        }
    });

    $.widget("ui.daystimepicker", {
        _create: function() {
            this.days = [];
            this._initDeck();
        },
        _initDeck: function() {
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
            timePicker = this.timePicker(day, month, year);

            if(this.days.length === 0) {
                this.days = [];
            }

            if(previous) {
                this.days.splice(
                    this.days.indexOf(previous) + 1, 0, $(timePicker).data("ui-myTimepicker")
                );
                $(previous.element).after(timePicker);
            } else {
                this.days.splice(
                    0, 0, $(timePicker).data("ui-myTimepicker")
                );
                $(this.daysContainer).prepend(timePicker);
            }
            if(this.days.length === 0) {
                $(this.labels).removeClass("active");
                $(this.labels).parents(".month-container").removeClass("hidden-arrows");
            } else {
                $(this.labels).addClass("active");
                $(this.labels).parents(".month-container").addClass("hidden-arrows");
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
        timePicker: function(day, month, year) {
            return $(dom("div", {"class": "my-time-picker"})).myTimepicker({
                day: day,
                month: month,
                year: year,
                container: this
            });
        }
    });

    $.widget("ui.myTimepicker", {
        options: {
            day: null,
            container: null
        },
        _create: function() {
            var that = this, timepickerOptions;

            this.label = dom("div", {"class": "day-value", "innerHTML": this.options.day});

            this.startTime = dom("input", {"class": "start-time"});
            this.endTime = dom("input", {"class": "end-time"});
            this.autoFill = dom("div", {"class": "checkbox autofill"});
            this.removeButton = dom("div", {"class": "remove"});
            this.daystimeContainer = this.options.container;

            $(this.element).append(this.label).append(this.startTime).append(this.endTime).append(this.autoFill).append(this.removeButton);

            function changeNext() {
                if(that.next()) {
                    if(that.next().isAutoFill()) {
                        that.next().setValue(
                        that.getValue());
                    }
                    that.next().changeNext()
                }
            };
            timepickerOptions = {
                onClose: changeNext,
                minutes: {
                    interval: 15
                },
                hours: {
                    starts: 0,
                    ends: 11
                },
                rows: 2,
                showPeriod: true,
                defaultTime: '1:00 PM'
            }

            $(this.startTime).timepicker(timepickerOptions);
            $(this.endTime).timepicker(timepickerOptions);

            $(this.removeButton).on('click', function() {
                if(confirm("Do you realy want to remove day?")) {
                    var format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(that.options.year, that.options.month - 1, that.options.day));
                    $(".days-picker", $(this).parents(".month-container")).multiDatesPicker('toggleDate', format_day);
                }
            });

            $(this.autoFill).on("click", function() {
                if(that.isFirst()){
                    $(this).toggleClass("checked");
                    if($(this).hasClass("checked")) {
                        that.autoFillAll();
                    } else {
                        that.removeAutoFillFromAll();
                    }
                } else {
                    $(this).toggleClass("checked");
                    if($(this).hasClass("checked")) {
                        that.setValue(that.previous().getValue());
                    } else {
                        that.setValue({
                            startTime: '',
                            endTime: ''
                        })

                    }
                }               
            });

            if($($('.autofill', this.daystimeContainer.daysContainer)[0]).hasClass("checked")){
                $(this.autoFill).trigger("click");
            }
        },
        isFirst: function(){
            return !this.previous();
        },
        autoFillAll: function(){
            var that=this, first=true;

            $('.autofill',this.daystimeContainer.daysContainer).each(function(){
                if(first){
                    first = false;
                    return;
                }
                if($(this).hasClass('checked')){
                    return;
                }
                if(that!=this){
                    $(this).trigger("click");
                }
            });
        },
        removeAutoFillFromAll: function(){
            var that=this, first=true;

            $('.autofill',this.daystimeContainer.daysContainer).each(function(){
                if(first){
                    first = false;
                    return;
                }
                if(!$(this).hasClass('checked')){
                    return;
                }
                if(that!=this){
                    $(this).trigger("click");
                }
            });
        },
        changeNext: function() {
            if(this.next()) {
                if(this.next().isAutoFill()) {
                    this.next().setValue(
                    this.getValue());
                }
                this.next().changeNext()
            }
        },      
        isAutoFill: function() {
            return $(this.autoFill).hasClass("checked")
        },
        previous: function() {
            return this.daystimeContainer.findPrevious(this.options.day);
        },
        next: function() {
            return this.daystimeContainer.findNext(this.options.day);
        },
        getValue: function() {
            return {
                startTime: $(this.startTime).val(),
                endTime: $(this.endTime).val()
            }
        },
        setValue: function(value) {
            $(this.startTime).val(value.startTime);
            $(this.endTime).val(value.endTime);
        }
    });

    $(document).ready(function() {
        setTimeout(function() {
            $('[data-event="click"] a').on("mousemove", function(e) {
                if(!('event' in window)) {
                    window.eventObj = e;
                }
            });
            $("#id_when").when();
            if($("#id_when_json").val()) {
                $("#id_when").data("ui-when").setValue(
                    JSON.parse(
                        $("#id_when_json").val()
                    )
                );
            };
        }, 100);
    });

})(jQuery);