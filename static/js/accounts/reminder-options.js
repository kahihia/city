;(function($, window, document, undefined) {
    'use strict';

    function ReminderOptionsPage(){
        $(".dropdown").qap_dropdown();
    }


    $(window).load(function(){
        window.reminderOptionsPage = new ReminderOptionsPage();
    });

})(jQuery, window, document);