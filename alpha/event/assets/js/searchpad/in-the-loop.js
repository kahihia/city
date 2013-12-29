;(function($, window, document, undefined) {
    'use strict';

    function InTheLoop(eventDetailsBlock){
        var that=this;
        this.eventElement = eventDetailsBlock;

        this.inTheLoopButton = $(".action-in-the-loop", this.eventElement);
        this.inTheLoopButton.on("click", this.openInTheLoopPopup.bind(this));

        this.saveTagsButton = $(".save-tags-button", this.eventElement);
        this.saveTagsButton.on("click", this.save.bind(this));        
        
        this.dialogContainer = $(".in-the-loop-popup", this.eventElement).dialog({
            dialogClass: "event-action-ui-dialog",
            resizable: false,
            width: 390,
            autoOpen: false
        });
    }

    InTheLoop.prototype = {
        openInTheLoopPopup: function(){
            $(this.dialogContainer).dialog("open");            
        },
        closeInTheLoopPopup: function(){
            $(this.dialogContainer).dialog("close");
        },
        save: function(eventId){
            var tags = $.map($(".tag:checked", this.dialogContainer).toArray(), function(element){
                        return $(element).data("tag");
                    });
            if(tags.length>0){
                $.ajax({
                    url: "/account-actions/add-in-the-loop/",
                    type: "GET",
                    data: { tag: tags },
                    dataType: "json",
                    success: function(data) {

                    }
                });
            }
            
            this.closeInTheLoopPopup();
        }
    }

    window.InTheLoop = InTheLoop;

})(jQuery, window, document);    