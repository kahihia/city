;(function($, window, document, undefined) {
    'use strict';

    function RemindMe(eventDetailsBlock){
        var that=this;
        this.eventElement = eventDetailsBlock;

        this.remindMeButton = $(".action-remind-me", this.eventElement);

        this.remindMeButton.on("click", function(){
            that.remindMe($(this).data("single-event-id"));
        });

        this.dialogContainer = $(".remind-me-popup", that.eventElement).dialog({
            dialogClass: "event-action-ui-dialog",
            resizable: false,
            width: 390,
            autoOpen: false
        });
    }

    RemindMe.prototype = {
        remindMe: function(eventId){
            var that=this;
            $.ajax({
                url: "/account-actions/remind-me/" + eventId + "/",
                dataType: "json",
                success: function(data) {
                    $(that.dialogContainer).dialog('open');
                }
            });
        }
    }

    window.RemindMe = RemindMe;

})(jQuery, window, document);    