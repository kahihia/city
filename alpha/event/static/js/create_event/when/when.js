;(function($, window, document, undefined) {
    var format = $.datepicker._defaults.dateFormat;

    function When(element){
        this.months = {
                //  2012: { 10: }
        };

        this.element = element;

        this.initDeck();
    }

    When.prototype = {
        initDeck: function() {
            var that = this,
                date = new Date();

            this.multiDayEvent = new MultiDayEvent(this);

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

            this.newMonthPicker = new NewMonthPicker(this.monthPicker, function(year, month){
                that.addMonth(year, month);
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
                    window.createEventPage.descriptionWidget.setDays(that.getDays());
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
                            daysPicker = this.months[yi][mi],
                            format_day, timesPicker;

                        daysPicker.addDay(parseInt(di), parseInt(mi), parseInt(yi));

                        format_day = $.datepicker.formatDate($.datepicker._defaults.dateFormat, new Date(yi, mi - 1, di));
                        $(".days-picker", $(daysPicker.element).parents(".months-container")).multiDatesPicker('addDates', format_day);

                        timesPicker = _.filter(daysPicker.days, function(day) {
                            return day.options.day == di;
                        })[0];

                        $(timesPicker.startTime).val(start);
                        $(timesPicker.endTime).val(end);

                        timesPicker.occurrences.load()
                    }
                }
            }
            $(this.element).val(this.getText());
        },
        addMonth: function(year, month) {
            var monthContainer, days, date, prevDaysPicker;

            if((year in this.months) && (month in this.months[year])) {
                return;
            }
            
            date = new Date();
            date.setDate(1);
            year && date.setFullYear(year);
            month && date.setMonth(month - 1);
            
            prevDaysPicker = this.findPrevDaysPicker(year, month);
            daysPicker = this.createMonthContainer(date, year, month);

            if(prevDaysPicker) {
                $(prevDaysPicker).after(daysPicker.monthContainer);
            } else {
                $(this.monthsContainer).prepend(daysPicker.monthContainer);
            }

            if(!(year in this.months)){
                this.months[year] = {};  
            }
            this.months[year][month] = daysPicker;
        },
        removeMonth: function(year, month) {
            delete this.months[year][month];
            if(this.months[year].length == 0) {
                delete this.months[year];
            }
        },
        findNextMonth: function(currentDaysPicker){
            var currentDetected = false;
            for(var yi in this.months) if(this.months.hasOwnProperty(yi)) {
                var months = this.months[yi];
                for(var mi in months) if(months.hasOwnProperty(mi)) {
                    var daysPicker = months[mi];
                    if(currentDetected) {
                        return daysPicker;
                    }
                    if(daysPicker==currentDaysPicker) {
                        currentDetected = true;
                    }
                }
            }
            return false;

        },
        findPrevDaysPicker: function(year, month) {
            var element;
            $(".month-container .days-picker").each(function() {
                if((year > this.year) || ((year == this.year) && (month > this.month))) {
                    element = $(this).parents(".month-container")[0];
                }
            });
            return element;
        },
        createMonthContainer: function(date, year, month) {
            var that = this,
                widget, daysPicker, daysPickerElement, multiSelectModeWrapper, removeButton, dayRangePicker, monthAndDaysWrapper, yesterday = (new Date());
            yesterday = yesterday.setDate(yesterday.getDate() - 1);

            monthAndDaysWrapper = dom("div", {"class": "month-and-days-wrapper"}, [
                multiSelectModeWrapper = dom("div", {"class": "multi-select-mode-wrapper"}, [
                    removeButton = dom("span", {"class": "remove"})
                ]),
                dayRangePicker = dom("div", {"class": "days-picker"})
            ]);            

            $(dayRangePicker).multiDatesPicker({
                onToggle: function(dateText) {
                    var dateArray = dateText.split("/"),
                        month = parseInt(dateArray[0]),
                        day = parseInt(dateArray[1]),
                        year = parseInt(dateArray[2]);

                    daysPicker.addDay(day, month, year);

                    if(daysPicker.days.length === 0) {
                        $(daysPicker.labels).removeClass("active");
                        $(daysPicker.labels).parents(".month-container").removeClass("hidden-arrows");
                    } else {
                        $(daysPicker.labels).addClass("active");
                        $(daysPicker.labels).parents(".month-container").addClass("hidden-arrows");
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

            dayRangePicker.year = year;
            dayRangePicker.month = month;

            $(removeButton).on("click", function() {
                if($(".month-container").length === 1) {
                    alert("You can not remove this month");
                    return;
                }
                if(confirm("Do you realy want to remove this month?")) {
                    that.removeMonth(dayRangePicker.year, dayRangePicker.month);
                    $(this).parents(".month-container").remove();
                }
            })            

            daysPickerElement = dom("div", {"class": "days-time-picker"});
            daysPicker = new DaysPicker(daysPickerElement, this);

            daysPicker.monthContainer =  dom("div", {"class": "month-container"}, [monthAndDaysWrapper, daysPickerElement]);

            return daysPicker;
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
            var value = {},
                occurrences = {};
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
                        if(times.hasMoreThanOneTime()){
                            var date = new Date(yi, mi - 1, times.options.day);
                            occurrences[$.datepicker.formatDate(format, new Date(date))] = times.getOccurrences();
                        }
                    }
                }
            }

            $("#id_when_json").val(JSON.stringify(value));
            $("#id_occurrences_json").val(JSON.stringify(occurrences));
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
            var json = this.getJson();            

            for(var yi in this.months) if(this.months.hasOwnProperty(yi)) {
                var months = this.months[yi];
                for(var mi in months) if(months.hasOwnProperty(mi)) {
                    var days = months[mi].days;
                    for(var di in days) if(days.hasOwnProperty(di)) {
                        var times = days[di];
                        if(!times.validate()) {
                            return false;
                        }
                    }
                }
            }
            
            return true;
        },
        clear: function(open) {
            $(this.deck).remove();
            this.months = {};
            this.initDeck();
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
            }

            $("#id_event_type").val(mode)
        }
    }

    window.When = When;

})(jQuery, window, document);