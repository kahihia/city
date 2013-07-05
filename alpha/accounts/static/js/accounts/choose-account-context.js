;(function($, window, document, undefined) {
    'use strict';

    function ChooseAccountContext(){
        var that=this;
        this.button = $(".choose-user-profile-button");
        this.popup = $(".choose-user-profile-popup");

        this.button.on("click", function(){
            that.popup.show();
        });

        $(document).on("click", this.closeIfNotPopup.bind(this));
    }

    ChooseAccountContext.prototype = {
        closePopup: function(e){
            this.popup.hide();
        },
        closeIfNotPopup: function(e){
            if($(e.target).hasClass("login-entry-info") || $(e.target).parents(".login-entry-info").length>0){
                
            } else {
                this.closePopup();
            }
        }
    };

    $(document).on("ready page:load", function(){
        window.chooseAccountContext = new ChooseAccountContext();
    });

})(jQuery, window, document);