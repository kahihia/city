;(function($, window, document, undefined) {
    'use strict';

    var format = $.datepicker._defaults.dateFormat,
        delimeter = /\b/;

    function sortByDays(obj){
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

    function DescriptionWidget(element){
        var that = this;

        element.descriptionWidget = this;
        
        this.data = {
            "default":"",
            days: {}
        };

        this.currentDay = "default";

        this.element = element;
        this.description = $("#id_description");
        this.textarea = $(this.element);
        this.dropdown = new Dropdown($(".description-dropdown")[0], {
            onChange: function(value, text){
                that.setCurrentDay(value, text);
            }
        });
        this.select = $("select", this.dropdown.element);
        

        $(this.element).on("blur", this.updateTags.bind(this));
        $(this.description).on("keyup", this.updateTags.bind(this));


        this.save();
        this.setupCKEditor();
    }

    DescriptionWidget.prototype = {
        updateTags: function(e){
            this.saveCurrentDay();
            if(this.currentDay=="default" && !delimeter.test(String.fromCharCode(e.keyCode))){
                $("#id_tags__tagautosuggest").data('ui-tagspopup').autoTagsDetect(
                    $("#id_description").val()
                );
            }
        },
        setValue: function(value){
            this.data = value;
            this.refreshWidget()
        },
        setDays: function(days){
            var oldDays = this.data.days;
            this.data.days = {};
            days.forEach(function(day, i){
                day = $.datepicker.formatDate(format, new Date(day));
                this.data.days[day] = oldDays[day] || "";
            }, this);

            this.refreshWidget();
            this.save();
        },
        sortDays: function(){
            this.data.days = sortByDays(this.data.days);
        },
        saveCurrentDay: function() {
            var days = this.data.days;
            $("#id_description").val(CKEDITOR.instances.id_description.getData()); 

            if(this.currentDay == "default") {
                for(var di in days){
                    var day = days[di];
                    if(day==this.data["default"]) {
                        days[di] = $(this.textarea).val();
                    }
                }
                this.data["default"] = $(this.textarea).val();
            } else {
                if(this.currentDay != this.select[0].options[this.select[0].selectedIndex].text) {
                    days[this.currentDay] = $(this.textarea).val();
                }
            }
            this.save();            
        },
        setCurrentDay: function(value, label){
            this.saveCurrentDay();

            this.currentDay = value;
            if(value == "default") {
                $(this.textarea).val(this.data["default"]);
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
               ['Table','-','Link','TextColor','BGColor','Source','Preview'],
               '/',
               ['NumberedList','BulletedList','-','Outdent','Indent','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock']
            ];

            CKEDITOR.config.contentsCss = '/static/styles/ckeditor-content.css';
            // CKEDITOR.config.filebrowserBrowseUrl = '/elfinder';

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
                    // e.data.html = e.data.dataValue.replace(/\s*width="[^"]*"/g, '');

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

                CKEDITOR.instances.id_description.on('change', function(e){
                    setTimeout(function(){ 
                        that.saveCurrentDay();
                    }, 1);
                });
            });
        },
        refreshWidget: function(){
            var days, that, select, defaultOption;
            this.sortDays();
            
            days = this.data.days;
            that = this;

            select = $("select", this.dropdown.element);
            select.empty();            

            defaultOption = dom("option", {
                value: "default",
                innerHTML: "Same for all"
            });

            select.append(defaultOption);

            for(var day in days) if(days.hasOwnProperty(day)){
                var option = dom("option", {
                    value: day,
                    innerHTML: $.datepicker.formatDate('D, M d', new Date(day))
                });

                select.append(option);
            }

            this.dropdown.refresh();
        }
    }

    window.DescriptionWidget = DescriptionWidget;    
})(jQuery, window, document);