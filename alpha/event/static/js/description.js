(function($) {
    var format = $.datepicker._defaults.dateFormat,
        delimeter = /\b/;
    $.widget("ui.description", {
        _create: function() {
            var that = this;
            this.textarea = $(this.element);
            this.selectDayWidget = $(".description-select-day-widget");
            this.toggler = $(".toggle", this.selectDayWidget);
            this.daysListContainer = $(".days-list", this.selectDayWidget);
            this.result = $(".result", this.selectDayWidget);
            this.selectedResult = $(".selected-result", this.selectDayWidget);
            this.descriptionDaysContainer = $(".description-days-container");

            $(this.toggler).on("click", function() {
                $(that.descriptionDaysContainer).toggleClass("active");
            });
            $(this.selectedResult).on("click", function() {
                $(that.daysListContainer).toggleClass("active");
            });
            $(this.element).on("change", function() {
                that.save();
            });
            $(this.element).on("blur", function(){
                that.saveCurrentDay();
            });
            $("#id_description").on("keyup", function(e){                
                if(that.currentDay=="default" && !delimeter.test(String.fromCharCode(e.keyCode))){
                    $("#id_tags__tagautosuggest").data('tagspopup').autoTagsDetect(
                        $("#id_description").val()
                    );
                    $("#id_description").focus();
                }               
            });

            this.data = {
                "default":"", 
                days: {}
            }
            this.currentDay = "default";
            this.save();

        },
        setValue: function(value){            
            this.data = value;
            this.drawWidget();
        },
        setDays: function(days) {
            var oldDays = this.data.days;
            this.data.days = {}
            for(var i in days) if(days.hasOwnProperty(i)) {
                var day = $.datepicker.formatDate(format, new Date(days[i]));
                this.data.days[day] = oldDays[day] || "";
            }
            this.drawWidget();
            this.save();
        },
        drawWidget: function() {
            var days = this.data.days,
                that = this;
            $(this.daysListContainer).empty();
            defaultWidget = $("<li>").attr("data-value", "default").html("Same for All");
            $(this.daysListContainer).append(defaultWidget);
            $(defaultWidget).on("click", function() {
                that.setCurrentDay("default", $(this).html());
            });
            for(var day in days) if(days.hasOwnProperty(day)) {
                var value = days[day],
                    dayWidget;
                dayWidget = $("<li>").attr("data-value", day);
                if(day == this.currentDay) {
                    $(dayWidget).addClass("selected");
                }
                $(dayWidget).html($.datepicker.formatDate('D, M d', new Date(day)));
                $(this.daysListContainer).append(dayWidget);
                dayWidget.day = day;
                $(dayWidget).on("click", function() {
                    that.setCurrentDay(
                        $(this).attr("data-value"), $(this).html()
                    );
                });
            }
            if(!(this.currentDay in this.selectedResult)) {
                this.setCurrentDay("default", "Same for All");
            }
        },
        saveCurrentDay: function() {
            var days = this.data.days;
            if(this.currentDay == "default") {
                this.data["default"] = $(this.textarea).val();
            } else {
                if(!(this.currentDay in this.selectedResult)) {
                    days[this.currentDay] = $(this.textarea).val();
                }
            }
            this.save();
        },
        setCurrentDay: function(value, label) {
            $(this.result).html(label);
            $(this.selectedResult).html(label);
            $(".selected", this.daysListContainer).removeClass("selected");
            this.saveCurrentDay();
            this.currentDay = value;
            if(value == "default") {
                $(this.textarea).val(this.data["default"]);
                $(this.result).html(label + " Days");
            } else {
                $(this.textarea).val(this.data.days[value] || "");                
            }
            $(this.textarea).attr("placeholder",this.data.days[value]||this.data["default"]);
            $("[data-value='" + value + "']").addClass("selected");
            this.save();
        },
        save: function() {
            $("#id_description_json").val(JSON.stringify(this.data));
        }
    });

    $(document).ready(function(){
        setTimeout(function(){
            var value = $("#id_description_json").val();
            $("#id_description").description();
            if(value){
                var json = JSON.parse(value);                
                $("#id_description").html(json["default"]);
                $("#id_description").data("description").setValue(json);
                $("#id_description").data("description").saveCurrentDay();
            }
        },100);
    });
})(jQuery);