;(function($, window, document, undefined) {
    'use strict';

    function ReportEvent(){
        var that=this;

        this.reportEventButton = $(".report-event-button");

        this.reportEventButton.on("click", function(){
            $(that.dialogContainer).dialog('open');
        });

        this.dialogContainer = $(".report-event-popup").dialog({
            dialogClass: "event-action-ui-dialog",
            resizable: false,
            width: 390,
            autoOpen: false
        });

        this.sendButton = $(".send-report-button");

        this.sendButton.on("click", this.sendReport.bind(this));
    }

    ReportEvent.prototype = {
        sendReport: function(){
            var that=this;

            $.ajax({
                url: "/cf-admin/report-event/",
                type: "POST",
                data: $(".report-event-popup form").serialize(),
                dataType: "json",
                success: function(data) {
                    window.ajaxPopup("Your report delivered. Thanx", 'success');
                    $(that.dialogContainer).dialog('close');
                }
            });
        }        
    }

    window.ReportEvent = ReportEvent;

})(jQuery, window, document);    