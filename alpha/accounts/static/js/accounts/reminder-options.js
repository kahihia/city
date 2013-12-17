;(function($, window, document, undefined) {
    'use strict';

    function ReminderOptionsPage(){
        $(".dropdown").qap_dropdown();

        $("[data-type=reminder_type_option]").on("click", function(){
            if($(this).prop('checked')) {
                $(this).parents("tr").addClass("active");
            }
            else {
                $(this).parents("tr").removeClass("active");
            }
        });

        var timepickerOptions = {
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

        $("#id_reminder_each_day_at_time").timepicker(timepickerOptions);
    }


    $(document).on("ready page:load", function(){
        window.reminderOptionsPage = new ReminderOptionsPage();
    });

})(jQuery, window, document);