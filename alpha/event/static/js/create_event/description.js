(function($) {
    var format = $.datepicker._defaults.dateFormat,
        delimeter = /\b/;

    sortByDays = function(obj){
        var keys = [];
        var sorted_obj = {};

        for(var key in obj){
            if(obj.hasOwnProperty(key)){
                keys.push(key);
            }
        }

        // sort keys
        keys.sort(function(first, second){
            var date1 = new Date(first),
                date2 = new Date(second);
            if (date1 > date2) return 1;
            if (date1 < date2) return -1;
            return 0;
        });

        // create new array based on Sorted Keys
        jQuery.each(keys, function(i, key){
            sorted_obj[key] = obj[key];
        });

        return sorted_obj;
    };

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
            // $(this.element).on("change", function() {
            //     that.save();
            // });
            $(this.element).on("blur", function(e){
                that.saveCurrentDay();
                if(that.currentDay=="default" && !delimeter.test(String.fromCharCode(e.keyCode))){
                    $("#id_tags__tagautosuggest").data('ui-tagspopup').autoTagsDetect(
                        $("#id_description").val()
                    );
                }
            });
            $("#id_description").on("keyup", function(e){
                if(that.currentDay=="default" && !delimeter.test(String.fromCharCode(e.keyCode))){
                    $("#id_tags__tagautosuggest").data('ui-tagspopup').autoTagsDetect(
                        $("#id_description").val()
                    );
                }
            });

            this.data = {
                "default":"",
                days: {}
            };

            this.currentDay = "default";
            this.save();
            this.setupCKEditor();
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
        sortDays: function(){            
            this.data.days = sortByDays(this.data.days);
        },
        drawWidget: function() {
            this.sortDays();
            
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
            $("#id_description").val(CKEDITOR.instances.id_description.getData()); 

            if(this.currentDay == "default") {
                for(var day_key in days){
                    var day = days[day_key];
                    if(day==this.data["default"]) {
                        days[day_key] = $(this.textarea).val();
                    }
                }
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
                $(this.textarea).val(this.data.days[value] || this.data["default"]);
            }            

            CKEDITOR.instances.id_description.setData($(this.textarea).val());

            $("[data-value='" + value + "']").addClass("selected");
            this.save();
        },
        save: function() {
            $("#id_description_json").val(JSON.stringify(this.data));
        },
        setupCKEditor: function(){
            var that=this;
            CKEDITOR.config.toolbar = [
               ['Styles','Format','Font','FontSize', 'Maximize'],
               '/',
               ['Bold','Italic','Underline','StrikeThrough','-','Undo','Redo'],
               ['Table','-','Link','TextColor','BGColor','Source'],
               '/',
               ['NumberedList','BulletedList','-','Outdent','Indent','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock']
            ];

            CKEDITOR.config.contentsCss = '/static/styles/ckeditor-content.css';

            CKEDITOR.replace("id_description");

            
            CKEDITOR.instances.id_description.on("instanceReady", function(){
                CKEDITOR.instances.id_description.on('key', function(e){
                    setTimeout(function(){
                        that.saveCurrentDay();
                        if(that.currentDay=="default" && !delimeter.test(String.fromCharCode(e.keyCode))){
                            $("#id_tags__tagautosuggest").data('ui-tagspopup').autoTagsDetect(
                                CKEDITOR.instances.id_description.getData()
                            );
                        }                        
                    }, 1);                    
                });

                CKEDITOR.instances.id_description.on('paste', function(e){
                    e.data.html = e.data.dataValue.replace(/\s*width="[^"]*"/g, '');

                    setTimeout(function(){ 
                        that.saveCurrentDay();
                        if(that.currentDay=="default" && !delimeter.test(String.fromCharCode(e.keyCode))){
                            $("#id_tags__tagautosuggest").data('ui-tagspopup').autoTagsDetect(
                                CKEDITOR.instances.id_description.getData()
                            );
                        }

                        that.updateWarning(
                            CKEDITOR.instances.id_description.getData()
                        );
                    }, 1);
                });
            });
        }        
    });

    $(document).ready(function(){
        setTimeout(function(){
            var value = $("#id_description_json").val();
            $("#id_description").description();
            if(value){
                var json = JSON.parse(value);
                $("#id_description").html(json["default"]);
                $("#id_description").data("ui-description").setValue(json);
                $("#id_description").data("ui-description").saveCurrentDay();
            }
        },100);
    });
})(jQuery);