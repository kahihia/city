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
    }


    $(document).on("ready page:load", function(){
        window.reminderOptionsPage = new ReminderOptionsPage();
    });

})(jQuery, window, document);