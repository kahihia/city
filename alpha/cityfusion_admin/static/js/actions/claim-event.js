;(function($, window, document, undefined) {
    'use strict';

    function ClaimEvent(){
        var that=this;

        this.claimEventButton = $(".claim-event-button");

        this.claimEventButton.on("click", function(){
            $(that.dialogContainer).dialog('open');
        });

        this.dialogContainer = $(".claim-event-popup").dialog({
            dialogClass: "event-action-ui-dialog",
            resizable: false,
            width: 390,
            autoOpen: false
        });

        this.sendButton = $(".send-claim-button");

        this.sendButton.on("click", this.sendClaim.bind(this));
    }

    ClaimEvent.prototype = {
        sendClaim: function(){
            var that = this;
            $.ajax({
                url: "/cf-admin/claim-event/",
                type: "POST",
                data: $(".claim-event-popup form").serialize(),
                dataType: "json",
                success: function(data) {
                    window.ajaxPopup("Your claim registered. Please wait.", 'success');
                    $(that.dialogContainer).dialog('close');
                }
            });
        }        
    }

    window.ClaimEvent = ClaimEvent;

})(jQuery, window, document);    