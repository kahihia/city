;(function($, window, document, undefined) {
    'use strict';

    function FeaturedSetupPage(){
        var start_date_input, end_date_input, days_to_display,
            that=this;

        start_date_input = $("#start_time_id");
        end_date_input = $("#end_time_id");
        days_to_display = $("#days_to_display");

        $.datepicker.initialized = false;
        $(".dropdown.date").on("click", function(){
            $("input", this).datepicker("show");
        });

        start_date_input.datepicker({
            minDate: new Date(),
            onSelect: function(){
                that.calculate_days_to_display();

            }
        });

        end_date_input.datepicker({
            minDate: new Date(),
            onSelect: function(){
                that.calculate_days_to_display();
            }
        });

        days_to_display.on("change", function(){
            that.calculate_end_date();

        });

        this.start_date_input = start_date_input;
        this.end_date_input = end_date_input;
        this.days_to_display = days_to_display;
    }

    FeaturedSetupPage.prototype = {
        calculate_days_to_display: function(){
            var date1 = this.start_date_input.datepicker('getDate'),
                date2 = this.end_date_input.datepicker('getDate'),
                diff = 1;
            if (date1 && date2) {
                diff = diff + Math.floor((date2.getTime() - date1.getTime()) / 86400000); // ms per day
            }
            this.days_to_display.val(diff);
        },
        calculate_end_date: function(){
            var start_date = this.start_date_input.datepicker('getDate'),
                date, month, year, days_to_display;

            days_to_display = +this.days_to_display.val();

            year = start_date.getFullYear();
            month = start_date.getMonth();
            date = start_date.getDate();

            this.end_date_input.val(
                $.datepicker.formatDate(
                    'mm/dd/yy',
                    new Date(year, month, date+days_to_display)
                )
            );
        }
        
    };

    $(document).on("ready page:load", function(){
        var ballons;
        window.featuredSetupPage = new FeaturedSetupPage();
        $.balloon.defaults.classname = "hintbox";
        $.balloon.defaults.css = {};
        ballons = $(".balloon");
        $(ballons).each(function(){
            var content = $(this).siblings(".balloon-content");
            $(this).balloon({
                contents:content,
                position:"left bottom",
                tipSize: 0,
                offsetX:0,//$.browser.msie?0:25,
                offsetY:25,//$.browser.msie?25:0,
                showDuration: 500, hideDuration: 0,
                showAnimation: function(d) { this.fadeIn(d); }
            });
        });
    });

})(jQuery, window, document);