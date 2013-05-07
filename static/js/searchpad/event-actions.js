;(function($, window, document, undefined) {
    'use strict';

    function InTheLoopPopup(button, popup){

    }

    function EventActions(eventDetailsBlock){
        var that=this;

        this.eventElement = eventDetailsBlock;

        this.remindMeButton = $(".action-remind-me", this.eventElement);
        this.inTheLoopButton = $(".action-in-the-loop", this.eventElement);
        this.inTheLoopPopup = $(".in-the-loop-tags-popup", this.eventElement);
        this.inTheLoopAddButton = $(".add-in-the-loop", this.InTheLoopPopup);

        this.remindMeButton.on("click", function(){
            that.remindMe($(this).data("event-id"));
        });

        this.inTheLoopButton.on("click", function(){
            that.openInTheLoopPopup();
        });

        this.initInTheLoopTags();

        this.inTheLoopAddButton.on("click", function(){
            that.saveInTheLoopTags();
        });
    }

    EventActions.prototype = {
        remindMe: function(eventId){
            $.ajax({
                url: "/account-actions/remind-me/" + eventId + "/" ,
                dataType: "html",
                success: function(data) {
                    window.ajaxPopup(data, 'success');
                }
            });
        },
        openInTheLoopPopup: function(){
            var that = this;
            $(this.inTheLoopPopup).fadeIn();
            setTimeout(function(){
                $(document).bind("click", that.closeInTheLoopListener=that.closeIfNotInTheLoopPopup.bind(that));

            },10);
        },
        closeInTheLoopPopup: function(e){
            $(this.inTheLoopPopup).fadeOut();
            $(document).unbind("click", this.closeInTheLoopListener);
        },
        closeIfNotInTheLoopPopup: function(e){
            if($(e.target).hasClass("in-the-loop-tags-popup") || $(e.target).parents(".in-the-loop-tags-popup").length>0){
                
            } else {
                this.closeInTheLoopPopup(e);
            }
        },
        initInTheLoopTags: function(){
            $(".tag", this.InTheLoopPopup).on("click", function(){
                $(this).toggleClass("active");
            });
        },
        saveInTheLoopTags: function(eventId){
            var tags = $.map($(".tag.active", this.InTheLoopPopup).toArray(), function(element){
                        return $(element).data("tag");
                    });
            if(tags.length>0){
                $.ajax({
                    url: "/account-actions/add-in-the-loop/",
                    type: "GET",
                    data: {
                        tag: $.map($(".tag.active", this.InTheLoopPopup).toArray(), function(element){
                            return $(element).data("tag");
                        })
                    },
                    dataType: "html",
                    success: function(data) {
                        window.ajaxPopup(data, 'success');
                    }
                });
            }
            
            this.closeInTheLoopPopup();
        }
    };



    window.EventActions = EventActions;

})(jQuery, window, document);