;(function($, window, document, undefined) {
    var format = $.datepicker._defaults.dateFormat;

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

    function Occurrences(myTimepicker){
        var that=this;
        this.myTimepicker = myTimepicker;

        this.times = [];

        this.addMoreTimeButton = dom("div", {"class": "add-new-time-button", "innerHTML": "+"});
        this.popup = dom("div", {"class": "multiple-time-event-popup", "innerHTML": "clicking this adds additional time(s) for this day"})

        $(this.addMoreTimeButton).on("mouseover", this.showPopup.bind(this));
        $(this.addMoreTimeButton).on("mouseout", this.hidePopup.bind(this));

        $(this.addMoreTimeButton).on("click", that.addMoreTime.bind(that));

        this.show();
    }

    Occurrences.prototype = {
        load: function(){
            var startTime = this.myTimepicker.getValue().startTime,
                endTime = this.myTimepicker.getValue().endTime,
                occurrences = JSON.parse($("#id_occurrences_json").val())[this.myTimepicker.getDate()],
                that = this;

            occurrences && occurrences.forEach(function(occurrence){
                if(occurrence.startTime!=startTime || occurrence.endTime!=endTime) {
                    var timesWidget = that.addMoreTime();
                    timesWidget.setValue(occurrence);
                }
            });
        },
        show: function(){
            $(this.myTimepicker.label).append(this.addMoreTimeButton);
            $(this.myTimepicker.label).append(this.popup);
            $(this.addMoreTimeButton).show();
        },
        hide: function(){
            if(this.addMoreTimeButton.parentNode) {
                this.addMoreTimeButton.parentNode.removeChild(this.addMoreTimeButton);
                this.popup.parentNode.removeChild(this.popup);
            }

            this.clear();
        },
        showPopup: function(){
            $(this.popup).show();
        },
        hidePopup: function(){
            $(this.popup).hide();
        },        
        addMoreTime: function(){
            var eventTimesWidget = new EventTimesWidget(this);
            this.times.push(eventTimesWidget);

            if(this.times.length==1) {
                $(this.myTimepicker.innerWrapper).after(eventTimesWidget.element);
            } else {
                $(this.times[this.times.length-2].element).after(eventTimesWidget.element);
            }

            return eventTimesWidget;
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
        getValue: function(){
            return _.map([this.myTimepicker].concat(this.times), function(dayTimePicker){
                return dayTimePicker.getValue();
            });
        },
        validate: function(){
            for(var i in this.times) if(this.times.hasOwnProperty(i)) {
                var day = this.times[i].getValue();
                if(!day.startTime || !day.endTime) return false;
            }
            return true;
        }
    }

    function TimesPicker(element, daysPicker, options){
        var that = this;

        this.element = element;
        this.options = options;     
        this.daysPicker = daysPicker;

        this.innerWrapper = dom("div", {"class": "my-time-picker-inner-wrapper"}, [
            this.label = dom("div", {"class": "day-value", "innerHTML": options.day}),
            this.startTime = dom("input", {"class": "start-time"}),
            this.endTime = dom("input", {"class": "end-time"}),
            this.autoFill = dom("div", {"class": "checkbox autofill"}),
            this.removeButton = dom("div", {"class": "remove"})
        ]);

        $(this.element).append(this.innerWrapper);

        this.occurrences = new Occurrences(this);

        timepickerOptions = {
            onClose: this.impactOnOtherDays.bind(this),
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
                var format_day = $.datepicker.formatDate(
                        $.datepicker._defaults.dateFormat, 
                        new Date(
                            that.options.year, 
                            that.options.month - 1, 
                            that.options.day
                        )
                    );

                $(".days-picker", $(this).parents(".month-container")).multiDatesPicker('toggleDate', format_day);
            }
        });

        $(this.autoFill).on("click", this.changeAutoFill.bind(this));
    }

    TimesPicker.prototype = {
        getDate: function(){
            var date = new Date(this.options.year, this.options.month - 1, this.options.day);
            return $.datepicker.formatDate(format, new Date(date));
        },
        validate: function(){
            var value = this.getValue();
            if(!value.startTime || !value.endTime) return false;
            return this.occurrences.validate();
        },
        isFirst: function(){
            return !this.previous();
        },
        impactOnOtherDays: function(){
            var isAutoFillOn = this.isAutoFill();
            if(this.isFirst()) {
                if(isAutoFillOn) {
                    this.copyToNext();
                }
            }
        },
        changeAutoFill: function(){
            $(this.autoFill).toggleClass("checked");
            var isAutoFillOn = this.isAutoFill();

            if(this.isFirst()) {
                if(isAutoFillOn) {
                    this.copyToNext();
                } else {
                    this.clearNext();
                }
            } else {
                if(isAutoFillOn) {
                    this.copyFromPrevious();
                } else {
                    this.clearValue()
                }
            }
        },
        setAutoFill: function(value){
            var functionName = value ? "addClass" : "removeClass";
            $(this.autoFill)[functionName]("checked");
        },
        copyToNext: function(){
            var next = this.next();
            if(next){
                next.setAutoFill(true);
                next.setValue(this.getValue());
                next.copyToNext();
            } else {
                if(this.nextMonth()) {
                    var first = this.nextMonth().findFirst();
                    if(first) {
                        first.setAutoFill(true);
                        first.setValue(this.getValue());
                        first.copyToNext();
                    }
                }
            }
        },
        copyFromPrevious: function(){
            this.setAutoFill(true);
            this.setValue(this.previous().getValue());
        },
        clearNext: function(){
            var next = this.next();
            if(next){
                next.setAutoFill(false);
                next.clearValue();
                next.clearNext();
            } else {
                if(this.nextMonth()) {
                    var first = this.nextMonth().findFirst();
                    if(first) {
                        first.setAutoFill(false);
                        first.clearValue();
                        first.clearNext();
                    }
                }
            }
        },
        clearValue: function(){
            this.setAutoFill(false);
            this.setValue({
                startTime: '',
                endTime: ''
            });
        },        
        isAutoFill: function() {
            return $(this.autoFill).hasClass("checked")
        },
        nextMonth: function(){
            return this.daysPicker.findNextMonth();
        },
        first: function(){
            return this.daysPicker.findFirst();
        },
        previous: function() {
            return this.daysPicker.findPrevious(this.options.day);
        },
        next: function() {
            return this.daysPicker.findNext(this.options.day);
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
        },
        hasMoreThanOneTime: function(){
            return this.occurrences.times.length > 0;
        },
        getDayUniqKey: function(){

        },
        getOccurrences: function(){
            return this.occurrences.getValue();
        }
    }

    window.TimesPicker = TimesPicker;

})(jQuery, window, document);