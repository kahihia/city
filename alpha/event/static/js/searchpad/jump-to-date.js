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

    var JumpToDate = function(){
        var that=this;
        this.openButton = $(".jump-popup-opener");
        this.popup = $(".jump-popup");

        this.openButton.on("click", this.openPopup.bind(this));
        $(document).on("click", this.closeIfNotPopup.bind(this));

        $(".time, .meridian").qap_dropdown();

        $(".start-date .date, .end-date .date").on("click", function(){
            $("input", this).datepicker("show");
        });

        $(".start-date .date input, .end-date .date input").datepicker();

        this.jumpLink = $(".jump-to-date-button");
        this.baseUrlQuery = this.jumpLink.data("base-url-query");

        this.bindChangeLinkEvents();

        this.timeJumpToDateCheckbox = $("#timeJumpToDateCheckbox");
        this.dateJumpToDateCheckbox = $("#dateJumpToDateCheckbox");

        this.timeJumpToDateCheckbox.on("change", function(){
            if($(this).is(':checked')) {
                $(".time-row .inline, .time-row .dropdown").removeAttr("disabled");
            } else {
                $(".time-row .inline, .time-row .dropdown").attr("disabled", true);
            }
        });

        this.dateJumpToDateCheckbox.on("change", function(){
            if($(this).is(':checked')) {
                $(".date-row .inline, .date-row .inline input").removeAttr("disabled");
            } else {
                $(".date-row .inline, .date-row  .inline input").attr("disabled", true);
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
            if($(e.target).hasClass("jump-popup") || $(e.target).parents(".jump-popup").length>0){
                
            } else {
                this.closePopup();
            }
        },
        bindChangeLinkEvents: function(){
            var that=this;
            $(".timepicker .dropdown", this.popup).on("dropdown.change", function(){
                that.changeLink();
            });

            $("input", this.popup).on("change", function(){
                that.changeLink();
            });

        },
        changeLink: function(){
            var startTime = $(".start-time .time select").val(),
                startMeridian = $(".start-time .meridian select").val(),
                endTime = $(".end-time .time select").val(),
                endMeridian = $(".end-time .meridian select").val(),
                startDate = $(".start-date .date input").val(),
                endDate = $(".end-date .date input").val(),
                href;

            if(startMeridian==="p.m."){
                startTime = (parseInt(startTime) + 12) +":00";
            }

            if(endMeridian==="p.m."){
                endTime = (parseInt(endTime) + 12) +":00";
            }

            if($(this.dateJumpToDateCheckbox).is(":checked") && $(this.timeJumpToDateCheckbox).is(":checked")){
                href = "{0}&start_date={1}&end_date={2}&start_time={3}&end_time={4}".format(
                    this.baseUrlQuery,
                    this.startOfDay(startDate), this.endOfDay(endDate),
                    startTime.replace(":00", ""), endTime.replace(":00", "")
                );
            } else if($(this.dateJumpToDateCheckbox).is(":checked")){
                href = "{0}&start_date={1}&end_date={2}".format(
                    this.baseUrlQuery,
                    this.startOfDay(startDate),
                    this.endOfDay(endDate)
                );
            } else if($(this.timeJumpToDateCheckbox).is(":checked")){
                href = "{0}&tart_time={1}&end_time={2}".format(
                    this.baseUrlQuery,
                    startTime.replace(":00", ""),
                    endTime.replace(":00", "")
                );
            } else {
                href = "javascript: void;";
            }

            $(this.jumpLink).attr("href", href);
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