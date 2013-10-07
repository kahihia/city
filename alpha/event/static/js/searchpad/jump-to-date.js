;(function($, window, document, undefined) {

    'use strict';

    String.prototype.format = String.prototype.f = function() {
        var s = this,
            i = arguments.length;

        while (i--) {
            s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
        }
        return s;
    };

    var JumpToDate = function(scope){
        var that=this;
        this.scope = scope;
        this.openButton = $(".jump-popup-opener", this.scope);
        this.popup = $(".jump-popup", this.scope);

        this.openButton.on("click", this.openPopup.bind(this));
        $(document).on("click", this.closeIfNotPopup.bind(this));

        $(".time, .meridian", this.scope).qap_dropdown();

        $.datepicker.initialized = false;
        $(".start-date .date, .end-date .date", this.scope).on("click", function(){
            $("input", this).datepicker("show");
        });

        $(".start-date .date input", this.scope).datepicker({
            onSelect: function (date) {
                var date2 = $('.start-date .date input').datepicker('getDate');
                date2.setDate(date2.getDate());
                $(".end-date .date input").datepicker('setDate', date2);
                //sets minDate to dt1 date + 1
                $(".end-date .date input").datepicker('option', 'minDate', date2);
            }
        });

        $(".end-date .date input", this.scope).datepicker({
            onClose: function () {
                var dt1 = $('.start-date .date input').datepicker('getDate');
                var dt2 = $('.end-date .date input').datepicker('getDate');
                //check to prevent a user from entering a date below date of dt1
                if (dt2 <= dt1) {
                    var minDate = $('.end-date .date input').datepicker('option', 'minDate');
                    $('.end-date .date input').datepicker('setDate', minDate);
                }
            }
        });

        this.jumpLink = $(".jump-to-date-button", this.scope);
        this.baseUrlQuery = this.jumpLink.data("base-url-query");

        this.bindChangeLinkEvents();

        this.startTimeJumpToDateCheckbox = $(".start-time-checkbox", this.scope);
        this.endTimeJumpToDateCheckbox = $(".end-time-checkbox", this.scope);
        this.dateJumpToDateCheckbox = $(".date-checkbox", this.scope);

        this.startTimeJumpToDateCheckbox.on("change", function(){
            if($(this).is(':checked')) {
                $(".start-time.inline, .start-time .dropdown", that.scope).removeAttr("disabled");
            } else {
                $(".start-time.inline, .start-time .dropdown", that.scope).attr("disabled", true);
            }
        });

        this.endTimeJumpToDateCheckbox.on("change", function(){
            if($(this).is(':checked')) {
                $(".end-time.inline, .end-time .dropdown", that.scope).removeAttr("disabled");
            } else {
                $(".end-time.inline, .end-time .dropdown", that.scope).attr("disabled", true);
            }
        });

        this.dateJumpToDateCheckbox.on("change", function(){
            if($(this).is(':checked')) {
                $(".date-row .inline, .date-row .inline input", that.scope).removeAttr("disabled");
            } else {
                $(".date-row .inline, .date-row  .inline input", that.scope).prop("disabled", true);
            }
        });

        this.jumpLink.on("click", function(){
            that.changeLink();
        });
    };

    JumpToDate.prototype = {
        openPopup: function(e){
            this.popup.show();
            this.openButton.addClass("active");
            e.stopPropagation();
        },
        closePopup: function(e){
            this.popup.hide();
            this.openButton.removeClass("active");
        },
        closeIfNotPopup: function(e){
            if(
                $(e.target).hasClass("jump-popup") || $(e.target).parents(".jump-popup").length>0 || $(e.target).parents("#ui-datepicker-div").length>0 || $(e.target).parents(".ui-datepicker-header").length>0
            ){
                
            } else {
                this.closePopup();
            }
        },
        bindChangeLinkEvents: function(){
            var that=this,
                startDateInput = $(".start-date .date input", this.popup),
                endDateInput = $(".end-date .date input", this.popup);;

            $(".timepicker .dropdown", this.popup).on("dropdown.change", function(){
                that.changeLink();
            });

            $("input", this.popup).on("change", function(){
                that.changeLink();
            });

            startDateInput.on("change", function(){
                var startDate = new Date(Date.parse(startDateInput.prop("value"))),
                    endDate = new Date(Date.parse(endDateInput.prop("value")));

                if(startDate>endDate){
                    endDateInput.val(startDateInput.val());
                }
            });

        },
        changeLink: function(){
            var startTime = $(".start-time .time select", this.scope).val(),
                startMeridian = $(".start-time .meridian select", this.scope).val(),
                endTime = $(".end-time .time select", this.scope).val(),
                endMeridian = $(".end-time .meridian select", this.scope).val(),
                startDate = $(".start-date .date input", this.scope).val(),
                endDate = $(".end-date .date input", this.scope).val(),
                href;

            startTime = parseInt(startTime);

            if(startMeridian==="p.m."){
                startTime += 12;
            }

            endTime = parseInt(endTime);

            if(endMeridian==="p.m."){
                endTime += 12;
            }

            if($(this.dateJumpToDateCheckbox).is(":checked") || $(this.startTimeJumpToDateCheckbox).is(":checked") || $(this.endTimeJumpToDateCheckbox).is(":checked")) {
                href = this.baseUrlQuery;

                if($(this.dateJumpToDateCheckbox).is(":checked")) {
                    href = href + "&start_date={0}&end_date={1}".format(this.startOfDay(startDate), this.endOfDay(endDate));
                }

                if($(this.startTimeJumpToDateCheckbox).is(":checked")){
                    href = href + "&start_time={0}".format(startTime);
                }
                if($(this.endTimeJumpToDateCheckbox).is(":checked")){
                    href = href + "&end_time={0}".format(endTime);
                }

            } else {
                href = "javascript: void;";
            }

            $(this.jumpLink).prop("href", href);
        },
        transformDate: function(date){
            var parts = date.split("/"), day, month, year;
            day = parts[1];
            month = parts[0];
            year = parts[2];
            return "{0}-{1}-{2}".format(year, month, day);
        },
        startOfDay:function(date){
            return "{0} 00:00:00".format(this.transformDate(date));
        },
        endOfDay: function(date){
            return "{0} 23:59:59".format(this.transformDate(date));
        }
    };

    window.JumpToDate = JumpToDate;

})(jQuery, window, document);