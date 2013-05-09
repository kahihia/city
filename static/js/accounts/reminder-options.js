;(function($, window, document, undefined) {
    'use strict';

    function ReminderOptionsPage(){
        $(".dropdown").qap_dropdown();

        $("input[name=reminder_active_type]").on("click", function(){
            $(".reminder-time-options .active").removeClass("active");
            $(this).parents("tr").addClass("active");
        });
    }


    $(document).on("ready page:load", function(){
        window.reminderOptionsPage = new ReminderOptionsPage();
    });

})(jQuery, window, document);